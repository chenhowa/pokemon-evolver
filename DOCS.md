# Pokemon Evolver REST API Documentation

## IMPORTANT USAGE NOTES
* The authenticated user can always use "me" in place of a trainer id. The trainer will simply be found through the id token instead of a direct id. For example,
    * GET /trainers/me
    * PATCH /trainers/me/pokemon/:pokemon_id
    * This method is slower than using the trainer id directly.
* In POST, PATCH, and PUT methods, only use properties that are listed in the accompanying scheme in the documentation. Using any other properties in the request body will result in returning 400 Bad Request.


## Viewing and Modifying the List of Trainers
#### POST, GET, PATCH, DELETE, PUT  /trainers/
* These methods are 403 Forbidden for the client. Clients do not have sufficient authority to do anything to the list of trainers directly.

## Getting, Updating, and Deleting a Specific Trainer
#### GET /trainers/:id
* If token is not valid, return 400 Bad Request
* If token does not match id, return 403 Forbidden
* If :id == "me"
    * If Trainer account exists, return it with 200 OK
    * If Trainer account does not exist, create it and return it with 200 OK.
* If :id != "me"
    * Get the associated Trainer account and return it with 200 OK.

#### PATCH /trainers/:id
* If token is not valid, return 400 Bad Request.
* If token does not match id, return 403 Forbidden
* If :id does not refer to an existing trainer, return 404 Not Found
* If :id refers to a valid trainer, patch its properties accordiing to the following scheme, and the patched Trainer is returned with 200 OK:

```
{
    'steps_walked': <optional integer>
    'total_evolves': <optional integer>
    'highest_level': <optional integer>
}
```

#### DELETE /trainers/:id
* If token is not valid, return 400 Bad Request.
* If token does not match id, return 403 Forbidden
* If :id does not refer to an existing trainer, return 404 Not Found
* If :id refers to a valid trainer, all the trainer's pokemon will be deleted, as will the trainer. Return 204 No Content.

## Getting, Deleting, and Adding to a Trainer's List of Pokemon
#### GET /trainers/:trainer_id/pokemon
* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, the entire list of the trainer's pokemon will be returned with 200 OK.
#### POST /trainers/:trainer_id/pokemon
* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, the server will create a new Pokemon for the trainer according to the following scheme, and then return it with 201 Created:

```
{
    "name": <required string>
}
```
### DELETE /trainers/:trainer_id/pokemon
* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to an existing trainer, the server will delete all the trainer's pokemon and return 204 No Content

## Getting, Updating, and Deleting a Trainer's Specific Pokemon
#### GET /trainers/:trainer_id/pokemon/:pokemon_id
* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, then
    * If :pokemon_id does not refer to one of the trainer's pokemon, return 400 Bad Request.
    * If :pokemon_id refers to one of the trainer's pokemon, return the pokemon with 200 OK.
#### PATCH /trainers/:trainer_id/pokemon/:pokemon_id
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
### DELETE /trainers/:trainer_id/pokemon/:pokemon_id
* If token is not valid, return 400 Bad Request
* If token does not match trainer_id, return 403 Forbidden.
* If :trainer_id does not refer to an existing trainer, return 404 Not Found
* If :trainer_id refers to a valid trainer, then
    * If :pokemon_id does not refer to one of the trainer's pokemon, return 400 Bad Request.
    * If :pokemon_id refers to one of the trainer's pokemon, the server will delete that specific pokemon and return 204 No Content

## Getting the List of All Pokemon
#### GET /pokemon
* Client does not have to be authenticated
* Returns a list of all pokemon in the server, but without any references to a pokemon's friends or a pokemon's current owner, with 200 OK. 

## Getting a Specific Pokemon
#### GET /pokemon/:id
* Client does not have to be authenticated.
* If :id does not refer to an existing pokemon, return 404 Not Found
* If : id refers to an existing pokemon, return the pokemon, but without any reference to its friends or its current owner, with 200 OK.

