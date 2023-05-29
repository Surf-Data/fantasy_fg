import pandas as pd
from datetime import date
from espn_api.baseball import League
import os
from dotenv import load_dotenv
load_dotenv()


class analyzer():
    def __init__(self,data,player_type='bat',free_agents=False):
        self.df = pd.DataFrame(data)#[['PlayerName','minpos','AB','PA','SLG','BB%','RBI','R','SB','K%','SO']]
        self.player_type = player_type
        self.free_agents = "True" == free_agents


        self.calcPoints()
        self.filters()
        self.df = self.df.sort_values('points',ascending=False
        ).reset_index(drop=True)


    
    def calcPoints(self):
        if self.player_type == 'bat':
            self.df['tb'] = self.df.SLG*self.df.AB
            self.df['walks'] = self.df['BB%']*self.df.PA
            self.df['Ks'] = self.df['K%']*self.df.PA
            self.df['points'] = self.df.tb +self.df.walks +self.df.SB-self.df.Ks+self.df.R+self.df.RBI
            self.df.points = self.df.points.astype(int)
        
        if self.player_type == 'sta':
            self.df['minpos'] ='P'
            self.df['points'] = (self.df.IP*3) - (self.df.ER*2) + (self.df.W*2) - (self.df.L*2) + (self.df.SV*5) + (self.df.SO) - (self.df.H) - (self.df.BB) + (self.df.HLD *2)
    
    def filters(self):
        if self.free_agents:
            self.get_free_agents()
        #self.df['ptsQuant'] = 100 - pd.qcut(self.df.points,100,labels=False)
        # g = self.df.groupby('minpos')
        # ranks = g.points.rank(method='min',ascending=False)
        # self.df['pointsPositionRank'] = ranks
        # self.df = self.df.loc[(self.df.pointsPositionRank<=20) | 
        #                       ((self.df.minpos == 'OF') & (self.df.pointsPositionRank<=40)) | 
        #                       ((self.df.minpos == 'P') & (self.df.pointsPositionRank<=120))
        #                       ].copy()
    def get_summary_stats(self):
        mean = self.df.points.mean()
        median = self.df.points.median()
        top_20 = self.df.loc[self.df.points.rank(method='min',ascending=False) <= 20].copy()
        top_20_mean = top_20.points.mean()
        top_20_median = top_20.points.median()

        return {"Mean":mean,"Median":median,"Top 20 Mean":top_20_mean,"Top 20 Median": top_20_median}

    def get_free_agents(self):
        try:
            l = league(league_id=os.environ['league_id']
               , year=2023
                ,espn_s2=os.environ['espn_s2']
                ,swid=os.environ['swid']
                )
        except Exception as E:
            print(E)

        position_id = None
        if self.player_type == 'sta':
            position_id = 14
        fas = l.free_agents(size=100,position_id=position_id)
        fa_names = []
        for fa in fas:
            fa_names.append(fa.name)
        self.df = self.df.loc[self.df.PlayerName.isin(fa_names)].copy()

    def calcVariances(self):
        pass
    

    def generate_html(self):
        return self.df[['PlayerName','points']].to_html()

    def generate_dict(self):
        return self.df[['PlayerName','points']].to_dict('records')

class league(League):
    pass


class startingPitcherGame():
    def __init__(self,frame_of_points):
        today = date.today()
        final_day = date(2023,10,1)
        diff  = final_day - today
        self.days_until_end = diff.days()
        self.n_teams = 10
        self.frame_of_points = frame_of_points
    def assign_teams(self,num_rounds):
        self.frame_of_points['teamGroup'] = -1
        for i in range(num_rounds):
            self.frame_of_points.loc['teamGroup'] = self.frame_of_points.index.apply(lambda x: x % 10)
            self.frame_of_points.groupby('teamGroup').points.rank(method='first',ascending=False)
        
    


