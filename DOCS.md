# Pokemon Evolver REST API Documentation

## IMPORTANT USAGE NOTES
* The authenticated user can always use "me" in place of a trainer id. The trainer will simply be found through the id token instead of a direct id. For example,
    * GET /trainers/me
    * PATCH /trainers/me/pokemon/:pokemon_id
    * This method is slower than using the trainer id directly.
* In POST, PATCH, and PUT methods, only use properties that are listed in the accompanying scheme in the documentation. Using any other properties in the request body will result in returning 400 Bad Request.

## Entities in this API
This section documents the Entities that exist in the backend database, and their important properties.

#### Trainer
Each trainer has 5 important properties:

* pokemon: list of the pokemon the trainer 'owns'.
* steps_walked: count of how many steps a trainer has walked.
* total_evolves: count of how many times a trainer has chosen to evolve a pokemon.
* highest_level: number representing the highest level pokemon a trainer has ever owned.
* region: the name of the trainer's current region in the Pokemon world.

#### Pokemon
Each pokemon has 7 important properties:

* current_owner: reference to its trainer
* name: name of the pokemon's species.
* nickname: name the trainer uses for the pokemon.
* level: number representing the pokemon's current level.
* xp: number representing the pokemon's experience within its current level.
* friends: list of pokemon that are 'friends' with this pokemon.
* gender: gender of the pokemon.

## Viewing and Modifying the List of Trainers
#### POST, GET, PATCH, DELETE, PUT  /trainers/
* These methods are 403 Forbidden for the client. Clients do not have sufficient authority to do anything to the list of trainers directly.

## Creating/Getting, Updating, and Deleting a Specific Trainer
#### GET /trainers/:id
This will get the trainer's account, or create it if it does not exist.

* If token is not valid, return 400 Bad Request
* If :id != "me" and token does not match :id, return 403 Forbidden
* If :id == "me"
    * If Trainer account exists, return it with 200 OK
    * If Trainer account does not exist, create it and return it with 200 OK.
* If :id != "me"
    * Get the associated Trainer account and return it with 200 OK, according to the following scheme:

```
{
    'pokemon': /* string[]; list of pokemon ids */,
    'steps_walked': /* int; number of steps walked */,
    'total_evolves': /* int; how many times the trainer has evolved pokemon */,
    'highest_level': /* int; the highest level pokemon a trainer has ever had */,
    'id': 'aabbc123' /* string; the trainer's particular id */
    'url': '/trainers/aabbc123' /* url to get trainer again if necessary */
    'region': /* string; name of trainer's region */
    
}
```
If :id (not "me") does not refer to a valid trainer account despite matching the valid token, return 400 Bad Request.

#### PATCH /trainers/:id
This will update a trainer's account if it exists.

* If token is not valid, return 400 Bad Request.
* If token does not match (a not "me") :id, return 403 Forbidden
* If :id does not refer to an existing trainer, return 404 Not Found. The account should've been obtained first with a call to GET /trainers/:id
* If :id refers to a valid trainer, patch its properties according to the following scheme, and the patched Trainer is returned with 200 OK:

```
{
    'steps_walked': <optional integer>
    'total_evolves': <optional integer>
    'highest_level': <optional integer>
    'region': <optional string>
}
```
See GET /trainers/:id for scheme of the returned Trainer.

#### DELETE /trainers/:id
This will delete a trainer's account if it exists.

* If token is not valid, return 400 Bad Request.
* If token does not match id, return 403 Forbidden
* If :id does not refer to an existing trainer, return 404 Not Found
* If :id refers to a valid trainer, all the trainer's pokemon will be deleted, as will the trainer. Return 204 No Content.

## Getting, Deleting, and Adding to a Trainer's List of Pokemon
#### GET /trainers/:trainer_id/pokemon
This gets a list of a trainer's pokemon, if the trainer exists.

* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, the entire list of the trainer's pokemon will be returned with 200 OK.
#### POST /trainers/:trainer_id/pokemon
This adds a pokemon to a trainer's list of pokemon, if the trainer exists.

* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, the server will create a new Pokemon for the trainer according to the following scheme, and then return it with 201 Created:

```
{
    "name": <required string>
}
```
#### DELETE /trainers/:trainer_id/pokemon
This deletes all the pokemon from a trainer's list of pokemon, if the trainer exists.

* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to an existing trainer, the server will delete all the trainer's pokemon and return 204 No Content

## Getting, Updating, and Deleting a Trainer's Specific Pokemon
#### GET /trainers/:trainer_id/pokemon/:pokemon_id
This gets a specific pokemon from a trainer, if the trainer exists.

* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, then
    * If :pokemon_id does not refer to one of the trainer's pokemon, return 400 Bad Request.
    * If :pokemon_id refers to one of the trainer's pokemon, return the pokemon with 200 OK.
#### PATCH /trainers/:trainer_id/pokemon/:pokemon_id
This updates a specific pokemon of a trainer, if the trainer exists.

* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, then
    * If :pokemon_id does not refer to one of the trainer's pokemon, return 400 Bad Request.
    * If :pokemon_id refers to one of the trainer's pokemon, then update it according to the following scheme and return it with 200 OK:

```
{
    'nickname': <optional string>
    'gender': <optional string>
    'level': <optional int>
    'xp': <optional int>
}
```
#### DELETE /trainers/:trainer_id/pokemon/:pokemon_id
This deletes a specific pokemon from a trainer and the server, if the trainer exists.

* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, then
    * If :pokemon_id does not refer to one of the trainer's pokemon, return 400 Bad Request.
    * If :pokemon_id refers to one of the trainer's pokemon, the server will delete that specific pokemon and return 204 No Content

# The following are implemented in the source code, but there wasn't time to test them in Postman or use them in the mobile frontend. Please disregard these for grading purposes.

## Getting the List of All Pokemon

#### GET /pokemon
This gets a sanitized list of all pokemon on the server.

* Client does not have to be authenticated
* Returns a list of all pokemon in the server, but without any references to a pokemon's friends or a pokemon's current owner, with 200 OK. 

## Getting a Specific Pokemon
#### GET /pokemon/:id
This gets a specific pokemon from the server, but sanitized for confidentiality of its owner.

* Client does not have to be authenticated.
* If :id does not refer to an existing pokemon, return 404 Not Found
* If : id refers to an existing pokemon, return the pokemon, but without any reference to its friends or its current owner, with 200 OK.


