# coding=utf-8
from datetime import datetime
import os
import re
import platform
import sys
from xml.dom import minidom
from nfo_utils import find_nfo_file_in_folder
from nfo_descriptor_file import NfoDescriptorFile


BUNDLE_NAME = "PlexNFO"
BUNDLE_VERSION = "1.0-001"


# PLEX Stuff
preferences = Prefs
PlexMovieAgent = Agent.Movies
Metadata = MetadataSearchResult
accepted_languages = [Locale.Language.NoLanguage]
PlexLogger = Log
# element_from_string = XML.ElementFromString
# MediaProxy = Proxy.Media
# Trailer = TrailerObject


def log(msg, *args, **kwargs):
    PlexLogger.Info(msg, *args, **kwargs)


def Start():
    log("{agent} v{ver} Loaded.".format(agent=BUNDLE_NAME, ver=BUNDLE_VERSION))
    log('Platform: %s %s', platform.system(), platform.release())
    log('Python: %s', sys.version)
    log('Preference[debug]: %s', preferences['debug'])
    
    return


class PLEXNFO(PlexMovieAgent):
    # @see:Framework.bundle/Contents/Resources/Versions/2/Python/Framework/api/agentkit.py / _push_agent_info (903)
    name = BUNDLE_NAME
    version = 0
    primary_provider = True
    languages = accepted_languages
    
    accepts_from = [
        'com.plexapp.agents.localmedia',
        'com.plexapp.agents.opensubtitles',
        'com.plexapp.agents.subzero'
    ]

    contributes_to = [
        'com.plexapp.agents.themoviedb',
        'com.plexapp.agents.imdb',
        'com.plexapp.agents.none'
    ]

    def search(self, results, media, lang, manual=False):
        log('*' * 120)
        log('*' * 55 + ': SEARCH :' + '*' * 55)
        log('*' * 120)
        
        try:
            movie_path = media.items[0].parts[0].file
        except:
            log("Unable to extract movie path from media object!")
            return
            
        log('Media title: %s', media.title)
        log('Media file: %s', movie_path)
        
        movie_folder = os.path.dirname(movie_path)
        nfo_path = find_nfo_file_in_folder(movie_folder)
        if nfo_path == None:
            log("Unable to find NFO file for this movie!")
            return
        
        log('NFO file: %s', nfo_path)
        NFO = NfoDescriptorFile(nfo_path)

        #Movie ID - Important to provide one even if not deined in NFO
        default_id = "abc-123" # hashnig needed on file path
        nfo_movie_id = NFO.get_id(default=default_id)
        nfo_movie_title = NFO.get_title()
        nfo_movie_year = NFO.get_year()
        
        result = Metadata(id=nfo_movie_id, name=nfo_movie_title, year=nfo_movie_year, lang=lang, score=100)
        results.Append(result)
        
        log("NFO Id: %s", nfo_movie_id)
        log("NFO Title: %s", nfo_movie_title)
        log("NFO Year: %s", nfo_movie_year)
        log('^' * 120)
        
        
    def update(self, metadata, media, lang):
        log('*' * 120)
        log('*' * 55 + ': UPDATE :' + '*' * 55)
        log('*' * 120)
        
        try:
            movie_path = media.items[0].parts[0].file
        except:
            log("Unable to extract movie path from media object!")
            return
            
        log('UPDATE ::: Title(%s):File(%s)', media.title, movie_path)
        
        movie_folder = os.path.dirname(movie_path)        
        nfo_path = find_nfo_file_in_folder(movie_folder)
        if nfo_path == None:
            log("Unable to find NFO file for this movie!")
            return
        
        log('Found NFO file: %s', nfo_path)
        
        NFO = NfoDescriptorFile(nfo_path)
        metadata.title = NFO.get_title()
        metadata.original_title = NFO.get_original_title(default=metadata.title)
        metadata.title_sort = NFO.get_sort_title(default=metadata.title)
        metadata.tagline = NFO.get_tagline()
        metadata.summary = NFO.get_plot()
        metadata.year = NFO.get_year()
        metadata.studio = NFO.get_studio()
        metadata.originally_available_at = NFO.get_premiered()
        metadata.rating = NFO.get_most_voted_rating()
        
        # Duration
        metadata.duration = NFO.get_runtime() * 60 * 1000  # convert min to ms
        
        #MPAA/Certification
        metadata.content_rating = NFO.get_mpaa(default='NR')
        
        # Writers (Credits)
        writer_list = NFO.get_credits()
        metadata.writers.clear()
        for writer in writer_list:
            metadata.writers.new().name = writer
            
        #Directors
        director_list = NFO.get_directors()
        metadata.directors.clear()
        for director in director_list:
            metadata.directors.new().name = director
        
        # Genres
        genre_list = NFO.get_genres()
        metadata.genres.clear()
        for genre in genre_list:
            metadata.genres.add(genre)
        
        # Countries
        country_list = NFO.get_countries()
        metadata.countries.clear()
        for country in country_list:
            metadata.countries.add(country)
        
        # Collections (Set)
        set_list = NFO.get_sets()
        metadata.collections.clear()
        for collectionset in set_list:
            metadata.collections.add(collectionset)
            
        # Actors
        actor_list = NFO.get_actors()
        metadata.roles.clear()
        for actor_item in actor_list:
            newrole = metadata.roles.new()
            newrole.name = actor_item["name"]
            newrole.role = actor_item["role"]
            newrole.photo = actor_item["thumb"]
            # Local Actor Image
            # img_file_name = actor_item["name"].replace(' ', '_') + '.jpg'
            # local_actor_img_path = os.path.join(movie_folder, '.actors', img_file_name)
            # local_actor_img_uri = "{}{}".format("http://localhost", local_actor_img_path)
            # log('Setting actor[%s] image path(1): %s', actor_item["name"], local_actor_img_path)
            # if not os.path.isfile(local_actor_img_path):
            #     local_actor_img_path = None
            # newrole.photo = local_actor_img_uri
            #log('Setting actor[%s] photo: %s', actor_item["name"], newrole.photo)
            
        
        self.dump_metadata_info(metadata)
        log('^' * 120)
        
        return metadata



    #log.debug('Set premiere to: {date}'.format(date=dt.strftime('%Y-%m-%d')))
    def dump_metadata_info(self, metadata):
        log('------------------------------------------------------------: MEDIA INFO :---')
        log('ID: %s', metadata.guid)
        log('Title: %s', metadata.title)
        log('Orginal Title: %s', metadata.original_title)
        log('Sort Title: %s', metadata.title_sort)
        log('Sort Tagline: %s', metadata.tagline)
        log('Sort Summary: %s', metadata.summary)
        log('Year: %s', metadata.year)
        log('Premiere: %s', metadata.originally_available_at) #.strftime('%Y-%m-%d')
        log('Studio: %s', metadata.studio)
        log('Duration(min): %s', metadata.duration / 60000)
        log('Content Rating: %s', metadata.content_rating)
        log('Rating: %s', metadata.rating)
        log('Writers: %s', [str(writer.name) for writer in metadata.writers])
        log('Directors: %s', [str(director.name) for director in metadata.directors])
        log('Genres: %s', [str(genre) for genre in metadata.genres])
        log('Countries: %s', [str(country) for country in metadata.countries])
        log('Collections: %s', [str(collection) for collection in metadata.collections])
        log('Actors: %s', [str(role.name) for role in metadata.roles])
        log('-----------------------------------------------------------------------------')
