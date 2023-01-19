import os
import re
from xml.dom import minidom
from dateutil.parser import parse

class NfoDescriptorFile():
    nfo_file_path = None
    nfo_movie = None
    
    def __init__(self, nfo_file_path):
        self.nfo_file_path = nfo_file_path
        if(os.path.isfile(self.nfo_file_path) is False):
            raise FileNotFoundError("NFO file does not exist! %s", self.nfo_file_path)
        
        nfo_data = minidom.parse(self.nfo_file_path)
        self.nfo_movie = nfo_data.getElementsByTagName('movie')[0]
        
    
    def get_id(self, default=None):
        return self.get_unique_root_element_value('id', default)
    
    def get_title(self, default=None):
        return self.get_unique_root_element_value('title', default)
    
    def get_sort_title(self, default=None):
        return self.get_unique_root_element_value('sorttitle', default)
    
    def get_original_title(self, default=None):
        return self.get_unique_root_element_value('originaltitle', default)
    
    # Not implemented yet...
    #def get_edition(self, default=None):
    #    return self.get_unique_root_element_value('edition', default)

    def get_tagline(self, default=None):
        return self.get_unique_root_element_value('tagline', default)
    
    def get_plot(self, default=None):
        return self.get_unique_root_element_value('plot', default)
    
    def get_outline(self, default=None):
        return self.get_unique_root_element_value('outline', default)
    
    def get_year(self, default=None):
        return int(self.get_unique_root_element_value('year', default))
    
    def get_mpaa(self, default=None):
        #<mpaa>DK:A</mpaa>
        return self.get_unique_root_element_value('mpaa', default)
    
    def get_certification(self, default=None):
        #<certification>DK:A</certification>
        return self.get_unique_root_element_value('certification', default)
    
    def get_studio(self, default=None):
        return str(self.get_unique_root_element_value('studio', default))
    
    def get_premiered(self, default=None):
        parsed_date = default
        try:
            date_str = str(self.get_unique_root_element_value('premiered', default))
            parsed_date = parse(date_str)
        except:
            pass
        return parsed_date
    
    def get_releasedate(self, default=None):
        parsed_date = default
        try:
            date_str = str(self.get_unique_root_element_value('releasedate', default))
            parsed_date = parse(date_str)
        except:
            pass
        return parsed_date  
    
    def get_runtime(self, default=0):
        return int(self.get_unique_root_element_value('runtime', default))
    
    def get_most_voted_rating(self, default=0.0):
        rating_value = default
        rating_votes = 0
        ratings = self.get_unique_root_element('ratings')
        try:
            for rating in ratings:
                votes = rating.getElementsByTagName('votes')[0].firstChild.data
                votes = int(str(votes).strip())
                if (votes > rating_votes):
                    rating_votes = votes
                    value = rating.getElementsByTagName('value')[0].firstChild.data
                    rating_value = float(str(value).strip())
        except:
            pass
        return rating_value
    
    def get_credits(self):
        director_list = []
        directors = self.get_unique_root_element('credits')
        for director in directors:
            name = str(director.firstChild.data).strip()
            director_list.append(name)
            
        return director_list
    
    def get_directors(self):
        director_list = []
        directors = self.get_unique_root_element('director')
        for director in directors:
            name = str(director.firstChild.data).strip()
            director_list.append(name)
            
        return director_list
    
    def get_genres(self):
        genre_list = []
        genres = self.get_unique_root_element('genre')
        for genre in genres:
            name = str(genre.firstChild.data).strip()
            genre_list.append(name)
            
        return genre_list
    
    def get_countries(self):
        country_list = []
        countries = self.get_unique_root_element('country')
        for country in countries:
            name = str(country.firstChild.data).strip()
            country_list.append(name)
            
        return country_list
    
    def get_sets(self):
        set_list = []
        sets = self.get_unique_root_element('set')
        for collectionset in sets:
            try:
                setname = collectionset.getElementsByTagName('name')[0].firstChild.data
                setname = str(setname).strip()
                set_list.append(setname)
            except:
                pass
            
        return set_list
    
    def get_actors(self):
        actor_list = []
        actors = self.get_unique_root_element('actor')
        for actor in actors:
            try:
                actor_item = {
                    "name": "",
                    "role": "", 
                    "thumb": "", 
                    "profile": "", 
                    "tmdbid": ""
                }
                if actor.getElementsByTagName('name')[0].firstChild:
                    actor_item["name"] = str(actor.getElementsByTagName('name')[0].firstChild.data).strip()
                if actor.getElementsByTagName('role')[0].firstChild:
                    actor_item["role"] = str(actor.getElementsByTagName('role')[0].firstChild.data).strip()
                if actor.getElementsByTagName('thumb')[0].firstChild:
                    actor_item["thumb"] = str(actor.getElementsByTagName('thumb')[0].firstChild.data).strip()
                if actor.getElementsByTagName('profile')[0].firstChild:
                    actor_item["profile"] = str(actor.getElementsByTagName('profile')[0].firstChild.data).strip()
                if actor.getElementsByTagName('tmdbid')[0].firstChild:
                    actor_item["tmdbid"] = str(actor.getElementsByTagName('tmdbid')[0].firstChild.data).strip()
                actor_list.append(actor_item)
            except:
                pass
        
        return actor_list
        
    
    def get_unique_root_element_value(self, tagname, default=None):
        try:
            node = self.get_unique_root_element(tagname)
            nodezero = node[0].firstChild
            value = str(nodezero.data).strip()
        except:
            value = default
            
        return value
    
    def get_unique_root_element(self, tagname):
        return self.nfo_movie.getElementsByTagName(tagname)
    
