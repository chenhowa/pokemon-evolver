

# main.py
# Howard Chen
# This document runs a REST API backend for the Pokemon Evolver app.
#


from google.appengine.ext import ndb # import database functionality on GAE
import webapp2 # import routing and request-handling framework
import json # import python's methods for handling JSON strings and objects with dictionaries
import httpcodes
import time
import random
from google.appengine.api import urlfetch

import jwt #to decode the id token string for use.



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
    print("SOURCE OF ERROR")
    print(id_token["sub"])
    print(ndb.Key(urlsafe=id).id())
    if id_token["sub"] != ndb.Key(urlsafe=id).id():
        return True

    return False

# NOT SECURE but I don't have time to learn how to get the key
# from the google certification discovery document!
def get_decoded_id_token(self):
    encoded = self.request.headers["Authorization"]
    print("ID TOKEN")
    id_token = jwt.decode(encoded, verify=False)
    return id_token

# Checks whether a token is NOT valid
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
        print("iss invalid")
        return True

    client_id = "130768413785-a9c800iouko8953344gvaf4oqq3jeket.apps.googleusercontent.com"
    if id_token["aud"] != client_id:
        print("aud invalid")
        return True

    # https://stackoverflow.com/questions/16755394/what-is-the-easiest-way-to-get-current-gmt-time-in-unix-timestamp-format
    # discusses how to get UNIX time in Python
    if id_token["exp"] <= time.time():
        print("token expired")
        return True

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
            print("Simulate verification of signature")

            # TO IMPLEMENT: ID TOKEN SIGNATURE VALIDATION


        else:
            # If we didn't get the discovery document, write an error to screen for 
            # testing.

            # Return false because we could not verify the token
            self.response.write("FAILED to retrieve discovery for some reason!");
            return True
    except urlfetch.Error:
        logging.exception('Caught an exception fetching discovery url')
        return True

    return False

# This function will udate a given ndb entity 
# using the key-specified value of the dictionary.
# returns the updated entity
class Pokemon(ndb.Model):
    current_owner = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    nickname = ndb.StringProperty()
    level = ndb.IntegerProperty()
    gender = ndb.StringProperty()
    xp = ndb.IntegerProperty()
    friends = ndb.JsonProperty(repeated=True) # List of secret:url pairs for viewing friend pokemon stats.

class Trainer(ndb.Model):
    region = ndb.StringProperty()
    pokemon = ndb.StringProperty(repeated=True) # List of pokemon ids.
    steps_walked = ndb.IntegerProperty()
    total_evolves = ndb.IntegerProperty()
    highest_level = ndb.IntegerProperty()

def validate_token_and_id(self, id, id_token):
    if token_not_valid(self, id_token):
        # Reject the request
        print("token invalid")
        self.response.write("bad token")
        httpcodes.write_bad_request(self)
        return False
    if id != "me":
        print("THE TRAINER ID IS")
        print(id)
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
    patch_properties = ['steps_walked', 'total_evolves', 'highest_level', 'region']

    @staticmethod
    def get_trainer(trainer_id, id_token):
        if trainer_id == "me":
            trainer = TrainerHandler.get_trainer_by_token(id_token)
            if not trainer:
                return None
        else:
            try:
                trainer = ndb.Key(urlsafe=trainer_id).get()
            except:
                return None
        return trainer

    @staticmethod
    def prep_trainer_dict(dict, id):
        dict['id'] = id;
        dict['url'] = '/trainers/' + id
        return dict

    @staticmethod
    def return_trainer_to_client(self, trainer):
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
                region="Kanto", id=id_token["sub"]) 
        trainer_key = new_trainer.put()
        return new_trainer

    def post(self, id=None):
        # This method is NOT ALLOWED for the client.
        # It doesn't make sense to allow them to
        # create their own account or anything
        write_method_not_allowed(self)
        return

    def get(self, id=None):
        try:
            id_token = get_decoded_id_token(self)
        except:
            httpcodes.write_bad_request(self)
            return

        # handles requests for trainer/account information
        if value_is_not_present(id):
            # Read-Access to all trainer accounts is not allowed
            httpcodes.write_method_not_allowed(self)
            return
        if validate_token_and_id(self, id, id_token) == False:
            print("NOT VALID")
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
                httpcodes.write_bad_request(self)
                return
        # Send back the trainer info
        print(trainer)
        TrainerHandler.return_trainer_to_client(self, trainer)
        httpcodes.write_ok(self)
        return

    def patch(self, id=None):
        try:
            id_token = get_decoded_id_token(self)
        except:
            httpcodes.write_bad_request(self)
            return

        # handles requests for trainer/account information
        if value_is_not_present(id):
            # Read-Access to all trainer accounts is not allowed
            print("NOT PRESENT")
            httpcodes.write_forbidden(self)
            return
        if validate_token_and_id(self, id, id_token) == False:
            print("INVALID")
            return
        # Check that the properties to patch are all valid
        new_data = json.loads(self.request.body)
        properties = new_data.keys()
        for p in properties:
            if p not in TrainerHandler.patch_properties:
                httpcodes.write_bad_request(self)
                return

        trainer = TrainerHandler.get_trainer(id, id_token)
        if not trainer:
            httpcodes.write_not_found(self)
            return

        # Once trainer is found, patch its properties
        # using the request data, and then save its data.
        for p in properties:
            trainer = update(trainer, new_data, p)
        trainer.put()

        TrainerHandler.return_trainer_to_client(self, trainer)
        httpcodes.write_ok(self)
        return

    def delete(self, id=None):
        try:
            id_token = get_decoded_id_token(self)
        except:
            httpcodes.write_bad_request(self)
            return

        # handles requests for trainer/account information
        if value_is_not_present(id):
            # Read-Access to all trainer accounts is not allowed
            httpcodes.write_forbidden(self)
            return
        if validate_token_and_id(self, id, id_token) == False:
            return

        trainer = TrainerHandler.get_trainer(id, id_token)
        if not trainer:
            httpcodes.write_not_found(self)
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
    required_post_properties = ['name']
    post_properties = ['name']
    patch_properties = ['nickname', 'gender', 'level', 'xp']

    def get(self, trainer_id=None, pokemon_id=None):
        print ("TRAINER HANDLER 2")
        try:
            id_token = get_decoded_id_token(self)
        except:
            httpcodes.write_bad_request(self)
            return

        if value_is_not_present(trainer_id):
            httpcodes.write_bad_request(self)
            return
        if validate_token_and_id(self, trainer_id, id_token) == False:
            return
        
        # Get the trainer before doing anything else
        trainer = TrainerHandler.get_trainer(trainer_id, id_token)
        if not trainer:
            print("TRAINER NOT FOUND")
            httpcodes.write_not_found(self)
            return

        if value_is_not_present(pokemon_id):
            print("GETTING POKEMON")
            # Then we just have the trainer id, and need to show his pokemon
            pokemon_list = ndb.get_multi(map(lambda p_id: ndb.Key(urlsafe=p_id),
                                            trainer.pokemon)) 
            pokemon_list = map(lambda p: PokemonHandler.prep_pokemon_dict_for_owner(p.to_dict(), p.key.urlsafe()), pokemon_list)

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
            PokemonHandler.return_pokemon_to_owner_client(self, pokemon)
            httpcodes.write_ok(self)
        return

    def put(self, trainer_id=None, pokemon_id=None):
        httpcodes.write_method_not_allowed(self)
        return

    def post(self, trainer_id=None, pokemon_id=None):
        try:
            id_token = get_decoded_id_token(self)
        except:
            print("exception in getting token")
            httpcodes.write_bad_request(self)
            return
        # handles requests for trainer/account information
        if value_is_not_present(trainer_id):
            httpcodes.write_forbidden(self)
            return
        if validate_token_and_id(self, trainer_id, id_token) == False:
            print("Exception in validating token")
            return
        if pokemon_id:
            # Can't post to a pokemon itself.
            httpcodes.method_not_allowed(self)
            return

        # Check that the properties for the post are all valid
        new_data = json.loads(self.request.body)
        properties = new_data.keys()
        for p in properties:
            if p not in TrainerHandler2.post_properties:
                print("bad property")
                httpcodes.write_bad_request(self)
                return
        for required in TrainerHandler2.required_post_properties:
            if required not in properties:
                print("bad required property")
                httpcodes.write_bad_request(self)
                return

        # Get the trainer and create a new pokemon for it
        trainer = TrainerHandler.get_trainer(trainer_id, id_token)
        print("TRAINER?")
        print(trainer)
        print(trainer.pokemon)
        if not trainer:
            httpcodes.write_not_found(self)
            return
        male = 0
        female = 1
        gender_int = random.randint(male, female)
        pokemon = Pokemon(current_owner=trainer.key.urlsafe(), name=new_data["name"],
                        nickname=new_data["name"], level=0, xp=0, friends=[])
        if gender_int == male:
            pokemon.gender = "male"
        elif gender_int == female:
            pokemon.gender = "female"
        pokemon_key = pokemon.put()
        pokemon_id = pokemon_key.urlsafe()
        trainer.pokemon.append(pokemon_id)
        trainer.put()

        # Return the newly created pokemon to the owner client
        PokemonHandler.return_pokemon_to_owner_client(self, pokemon)
        httpcodes.write_created(self)
        return

    def patch(self, trainer_id=None, pokemon_id=None):
        try:
            id_token = get_decoded_id_token(self)
        except:
            httpcodes.write_bad_request(self)
            return

        if value_is_not_present(trainer_id):
            httpcodes.write_bad_request(self)
            return
        if validate_token_and_id(self, trainer_id, id_token) == False:
            return
        if value_is_not_present(pokemon_id):
            # Not allowed to patch the entire list of a trainer's pokemon
            httpcodes.write_forbiddent(self)
            return

        # Get the trainer before doing anything else
        trainer = TrainerHandler.get_trainer(trainer_id, id_token)
        if not trainer:
            httpcodes.write_not_found(self)
            return

        # Get the patch data and check it is all valid
        new_data = json.loads(self.request.body)
        properties = new_data.keys()
        for p in properties:
            if p not in TrainerHandler2.patch_properties:
                print("PROPERTY NOT FOUND")
                write_bad_request(self)
                return

        # If a specific pokemon is given to patch, then patch it
        if pokemon_id not in trainer.pokemon:
            print("POKEMON NOT FOUND")
            httpcodes.write_bad_request(self)
            return
        pokemon = ndb.Key(urlsafe=pokemon_id).get()

        for p in properties:
            pokemon = update(pokemon, new_data, p)
        pokemon.put()

        PokemonHandler.return_pokemon_to_owner_client(self, pokemon)
        httpcodes.write_ok(self)
        return


    def delete(self, trainer_id=None, pokemon_id=None):
        try:
            id_token = get_decoded_id_token(self)
        except:
            httpcodes.write_bad_request(self)
            return
        if value_is_not_present(trainer_id):
            httpcodes.write_bad_request(self)
            return
        if validate_token_and_id(self, trainer_id, id_token) == False:
            return

        # Get the trainer before doing anything else
        trainer = TrainerHandler.get_trainer(trainer_id, id_token)
        if not trainer:
            httpcodes.write_not_found(self)
            return

        if value_is_not_present(pokemon_id):
            # Then we just need to delete ALL the trainer's pokemon
            for p_id in trainer.pokemon:
                p_key = ndb.Key(urlsafe=p_id)
                p_key.delete()
            trainer.pokemon = []
        else:
            # Then we have a specific pokemon to delete
            if pokemon_id not in trainer.pokemon:
                httpcodes.write_bad_request(self)
                return
            ndb.Key(urlsafe=pokemon_id).delete()
            trainer.pokemon = [p for p in trainer.pokemon if p != pokemon_id]

        trainer.put()
        httpcodes.write_no_content(self)
        return


class PokemonHandler(webapp2.RequestHandler):
    @staticmethod
    def get_all_pokemon():
        return Pokemon.query().fetch()

    @staticmethod
    def prep_pokemon_dict_for_owner(dict, id):
        dict['id'] = id
        dict['url'] = '/pokemon/' + id
        return dict

    @staticmethod
    def prep_pokemon_dict_for_stranger(dict, id):
        dict = PokemonHandler.prep_pokemon_dict_for_owner(dict, id)
        del dict['friends']
        del dict['current_owner']
        return dict

    @staticmethod
    def return_pokemon_to_stranger_client(self, pokemon):
        pokemon_id = pokemon.key.urlsafe()
        pokemon_dict = pokemon.to_dict()
        pokemon_dict = PokemonHandler.prep_pokemon_dict_for_stranger(pokemon_dict, pokemon_id)
        self.response.write(json.dumps(pokemon_dict))

    @staticmethod
    def return_pokemon_to_owner_client(self, pokemon):
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
                pokemon = ndb.Key(urlsafe=id).get()
            except:
                # If pokemon was not found, inform client
                httpcodes.write_not_found(self)
                return
            PokemonHandler.return_pokemon_to_stranger_client(self, pokemon)
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
    ('/trainers/(.*)/pokemon(/?)', TrainerHandler2),
    ('/trainers/(.*)/pokemon/(.*)', TrainerHandler2),
    ('/trainers(/?)', TrainerHandler),
    ('/trainers/(.*)', TrainerHandler),

    ('/pokemon(/?)', PokemonHandler),
    ('/pokemon/(.*)', PokemonHandler)
], debug=True)

