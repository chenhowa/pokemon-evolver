

# main.py
# Howard Chen
# This document runs a REST API backend for the Pokemon Evolver app.
#
# New user flow: The authenticated 


from google.appengine.ext import ndb # import database functionality on GAE
import webapp2 # import routing and request-handling framework
import json # import python's methods for handling JSON strings and objects with dictionaries
import httpcodes
import time()
from google.appengine.api import urlfetch



# Set up cachine. For testing purposes. we set caching to be OFF.
context = ndb.get_context()
context.set_cache_policy(False)
context.set_memcache_policy(False)

def value_is_not_present(val):
    if val:
        return False 
    return True

def id_not_valid(self, id, id_token):
    # if the id doesn't match the token identifier, the id isn't valid
    if id_token["sub"] != ndb.Key(urlsafe=id).id():
        return False

    return True

def token_not_valid(self, id_token):
    valid_iss_strings = [
        "https://accounts.google.com",
        "accounts.google.com"
            ]
    iss_is_valid = False
    for iss in valid_iss_strings:
        if id_token["iss"] == iss:
            iss_is_valid = True
            break
    if not iss_is_valid:
        return False

    client_id = "130768413785-a9c800iouko8953344gvaf4oqq3jeket.apps.googleusercontent.com"
    if id_token["aud"] != client_id:
        return False

    # https://stackoverflow.com/questions/16755394/what-is-the-easiest-way-to-get-current-gmt-time-in-unix-timestamp-format
    # discusses how to get UNIX time in Python
    if id_token["exp"] >= time.time():
        return False

    # Finally, fetch AND CACHE the discovery document and use it 
    # to verify that the token is signed correctly
    discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
    headers = {'Cache-Control': 'public'}
    try:
        result = urlfetch.fetch(
                url=discovery_url,
                method=urlfetch.GET,
                headers=headers)
        if result.status_code == 200:
            # We should have the discovery document. Attempt to verify the token


            # TO IMPLEMENT: ID TOKEN SIGNATURE VALIDATION


        else:
            # If we didn't get the discovery document, write an error to screen for 
            # testing.

            # Return false because we could not verify the token
            self.response.write("FAILED to retrieve discovery for some reason!");
            return False
    except urlfetch.Error:
        logging.exception('Caught an exception fetching discovery url')
        return False

    return True

# This function will udate a given ndb entity 
# using the key-specified value of the dictionary.
# returns the updated entity
class Pokemon(ndb.Model):
    current_owner = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    level = ndb.IntegerProperty()
    gender = ndb.StringProperty()
    xp = ndb.IntegerProperty()
    friends = ndb.JsonProperty(repeated=True) # List of secret:url pairs for viewing friend pokemon stats.

class Trainer(ndb.Model):
    pokemon = ndb.StringProperty(repeated=True) # List of pokemon ids.
    steps_walked = ndb.IntegerProperty()
    total_evolves = ndb.IntegerProperty()
    highest_level = ndb.IntegerProperty()

def validate_token_and_id(self, id, id_token):
    if token_not_valid(self, id_token):
        # Reject the request
        httpcodes.write_bad_request(self)
        return False
    if id != "me":
        if id_not_valid(self, id, id_token):
            # If the id doesn't match the OpenId Connect Token info, or if 
            # the token info is simply not valid accordiing to Google, reject the call.
            httpcodes.write_forbidden(self)
            return False
    return True

def update(ndb_entity, data_dict, key):
    name = data_dict.get(key)
    if name:
        # If the data_dict had the key property, the entity
        # will now have it as well
        setattr(ndb_entity, key, name)
    
    # Regardless of what happens, return the entity
    return ndb_entity

class TrainerHandler(webapp2.RequestHandler):
    patch_properties = ['steps_walked', 'total_evolves', 'highest_level', 'pokemon']

    @staticmethod
    def prep_trainer_dict(dict, id):
        dict['id'] = id;
        dict['url'] = '/trainers/' + id
        return dict

    @staticmethod
    def return_trainer_to_client(trainer)
        trainer_id = trainer.key.urlsafe()
        trainer_dict = trainer.to_dict()
        trainer_dict = TrainerHandler.prep_trainer_dict(trainer_dict, trainer_id)
        self.response.write(json.dumps(trainer_dict))

    @staticmethod
    def get_trainer_by_token(id_token):
        return Trainer.get_by_id(id_token["sub"])

    @staticmethod
    def  prep_delete(trainer):
        for poke_id in trainer.pokemon:
            try:
                pokemon = ndb.Key(urlsafe=poke_id).get()
                PokemonHandler.prep_delete(pokemon)
                pokemon.key.delete()
            except:
                # If trainer owns a pokemon that doesn't exist, get rid of that id and
                # report a bad state error to client
                trainer.pokemon = [p for p in trainer.pokemon if p != poke_id]
                return False


    # This creates a trainer entity and an account entity 
    # associated with the trainer. This allows a trainer to
    # retrieve their entities with just an id token that is 
    # used to access the account entity
    @staticmethod
    def create_trainer_by_token(id_token):
        # This may not be safe, but it's faster to just use the unique Google identifier
        # as the key for the new trainer. Fewer calls to the Datastore are required.
        new_trainer = Trainer(pokemon=[], steps_walked=0, total_evolves=0, highest_level=0,
                id=id_token["sub"]) 
        trainer_key = new_trainer.put()
        return new_trainer

    def post(self, id=None):
        # This method is NOT ALLOWED for the client.
        # It doesn't make sense to allow them to
        # create their own account or anything
        write_method_not_allowed(self)

    def get(self, id=None):
        # First, validate everything related to the token
        id_token = json.loads(self.request.headers["Authorization"])

        # handles requests for trainer/account information
        if value_is_not_present(id):
            # Read-Access to all trainer accounts is not allowed
            httpcodes.write_forbidden(self)
            return
        if validate_token_and_id(self, id, id_token) == False:
            return

        # The id is valid, and we can use it.
        if id == "me":
            # use the token to search for and access the account's Trainer Entity
            trainer = TrainerHandler.get_trainer_by_token(id_token)
            if not trainer:
                trainer = TrainerHandler.create_trainer_by_token(id_token)
        else:
            # We work under the assumption that the client has already
            # created a valid account represented by the id.
            # Hence it is an error if the client tries to access a Trainer 
            # that doesn't exist.
            try:
                trainer_key = ndb.Key(urlsafe=id)
                trainer = trainer_key.get()
            except:
                #If trainer key cannot be obtained, reject the request
                httpcodes.write_bad_request
                return
        # Send back the trainer info
        TrainerHandler.return_trainer_to_client(trainer)
        httpcodes.write_ok(self)
        return

    def patch(self, id=None):
        # First, validate everything related to the token
        id_token = json.loads(self.request.headers["Authorization"])

        # handles requests for trainer/account information
        if value_is_not_present(id):
            # Read-Access to all trainer accounts is not allowed
            httpcodes.write_forbidden(self)
            return
        if validate_token_and_id(self, id, id_token) == False:
            return
        # Check that the properties to patch are all valid
        new_data = json.loads(self.request.body)
        properties = new_data.keys()
        for p in properties:
            if p not in TrainerHandler.patch_properties:
                write_bad_request(self)
                return

        if id == "me":
            trainer = TrainerHandler.get_trainer_by_token(id_token)
            if not trainer: 
                # If there's no trainer, we cannot perform patch
                httpcodes.write_not_found(self)
                return
        else:
            try:
                trainer = ndb.Key(urlsafe=id).get()
            except:
                # If no trainer is found, tell client
                httpcodes.write_not_found(self)
                return
        # Once trainer is found, patch its properties
        # using the request data, and then save its data.
        for p in properties:
            trainer = update(trainer, new_data, p)
        trainer.put()

        TrainerHandler.return_trainer_to_client(trainer)
        httpcodes.write_ok(self)
        return

    def delete(self, id=None):
        # First, validate everything related to the token
        id_token = json.loads(self.request.headers["Authorization"])

        # handles requests for trainer/account information
        if value_is_not_present(id):
            # Read-Access to all trainer accounts is not allowed
            httpcodes.write_forbidden(self)
            return
        if validate_token_and_id(self, id, id_token) == False:
            return


        if id == "me":
            trainer = TrainerHandler.get_trainer_by_token(id_token)
            if not trainer:
                # If there's no trainer, there was nothing to delete
                http_codes.write_not_found(self)
                return
        else:
            try:
                trainer = ndb.Key(urlsafe=id).get()
            except:
                http_codes.write_not_found(self)
                return
        # Once you have the key, use it to delete all the trainer's pokemon AND 
        # delete the trainer.
        sucess_flag = TrainerHandler.prep_delete(trainer)
        if success_flag == False:
            httpcodes.write_conflict(self)
            return

        trainer.key.delete()
        httpcodes.write_no_content(self)
        return

    def put(self, id=None):
        # There's nothing to put for /trainers/ or /trainers/:id/
        write_forbidden(self)
        return

class TrainerHandler2(webapp2.RequestHandler):
    required_post_properties = ["name"]
    post_properties = ["name"]

    # patch_properties do not include friends, which are added 1 at a time
    patch_properties = ["name", "level", "gender", "xp"]

    def get(self, trainer_id=None, pokemon_id=None):
        # First, validate everything related to the token
        id_token = json.loads(self.request.headers["Authorization"])

        if value_is_not_present(trainer_id):
            httpcodes.write_bad_request(self)
            return
        if validate_token_and_id(self, trainer_id, id_token) == False:
            return
        
        # Get the trainer before doing anything else
        if trainer_id == "me":
            trainer = TrainerHandler.get_trainer_by_token(id_token)
            if not trainer:
                httpcodes.write_not_found(self)
                return
        else:
            try:
                trainer = ndb.Key(urlsafe=trainer_id).get()
            except:
                httpcodes.write_not_found(self)
                return

        if value_is_not_present(pokemon_id):
            # Then we just have the trainer id, and need to show his pokemon
            pokemon_list = ndb.get_multi(map(lambda p_id: ndb.Key(urlsafe=p_id),
                                            trainer.pokemon)) 
            pokemon_list = map(lambda p: PokemonHandler.prep_pokemon_dict_for_owner(p.to_dict(), p.key.id), pokemon_list)

            self.response.write(json.dumps(pokemon_list))
            httpcodes.write_ok(self)
        else:
            # Then we have trainer and pokemon id, and need to show the specific pokemon
            
            # Verify that the pokemon in fact belongs to the trainer
            if pokemon_id not in trainer.pokemon:
                httpcodes.write_bad_request(self)
                return

            # If pokemon belongs to trainer, then send it to the trainer!
            try:
                pokemon = ndb.Key(urlsafe=pokemon_id).get()
            except:
                # Pokemon was somehow accidentally deleted! Let client know to try again
                trainer.pokemon = [p for p in trainer.pokemon if p != pokemon_id]
                httpcodes.write_conflict(self)
                return
            PokemonHandler.return_pokemon_to_owner_client(pokemon)
            httpcodes.write_ok(self)
        return

class PokemonHandler(webapp2.RequestHandler):
    @staticmethod
    def get_all_pokemon():
        return Pokemon.query().fetch()

    @staticmethod
    def prep_pokemon_dict_for_owner(dict, id):
        dict['id'] = id
        dict['url'] = '/pokemon/ + id'
        return dict

    @staticmethod
    def prep_pokemon_dict_for_stranger(dict, id):
        dict = PokemonHandler.prep_pokemon_dict_for_owner(dict, id)
        del dict['friends']
        del dict['current_owner']
        return dict

    @staticmethod
    def return_pokemon_to_stranger_client(pokemon):
        pokemon_id = pokemon.key.urlsafe()
        pokemon_dict = pokemon.to_dict()
        pokemon_dict = PokemonHandler.prep_pokemon_dict_for_stranger(pokemon_dict, pokemon_id)
        self.response.write(json.dumps(pokemon_dict))

    @staticmethod
    def return_pokemon_to_owner_client(pokemon):
        pokemon_id = pokemon.key.urlsafe()
        pokemon_dict = pokemon.to_dict()
        pokemon_dict = PokemonHandler.prep_pokemon_dict_for_owner(pokemon_dict, pokemon_id)
        self.response.write(json.dumps(pokemon_dict))

    def post(self, id=None):
        # Pokemon cannot be created through this handler
        # since users are not authenticated
        httpcodes.write_forbidden(self)
        return

    def get(self, id=None):
        if value_is_not_present(id):
            # Query for all pokemon and return sanitized list to client
            sanitized_list = map(lambda p: PokemonHandler.prep_pokemon_dict_for_stranger(
                            p.to_dict(), p.key.urlsafe() ), PokemonHandler.get_all_pokemon() )
            self.response.write(json.dumps(sanitized_list))
            httpcodes.write_ok(self)
            return
        else:
            try: 
                pokemon = ndb.Key(urlsafe=id)
            except:
                # If pokemon was not found, inform client
                httpcodes.write_not_found(self)
                return
            PokemonHandler.return_pokemon_to_stranger_client(pokemon)
            httpcodes.write_ok(self)
            return

    def patch(self, id=None):
        # No modifications to pokemon are allowed, since client is not 
        # authenticated here.
        httpcodes.write_forbidden(self)
        return

    def put(self, id=None):
        httpcodes.write_forbidden(self)
        return

    def delete(self, id=None):
        # An unauthenticated user is DEFINITELY NOT ALLOWED to do deletions
        httpcodes.write_forbidden(self)
        return

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Hello, Pokemon Evolver! (HC)")


# Add the patch method to the allowed HTTP verbs
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/trainers/(.*)/pokemon/', TrainerHandler2),
    ('/trainers/(.*)/pokemon/(.*)', TrainerHandler2),
    ('/trainers/', TrainerHandler),
    ('/trainers/(.*)', TrainerHandler),

    ('/pokemon/', PokemonHandler),
    ('/pokemon/(.*)', PokemonHandler)
], debug=True)

