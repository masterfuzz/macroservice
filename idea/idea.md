# Idea

Explore the microservice/monolith dichotomy and "alternative" paradigms

# Macroservice

The "client - client" model - aka "serverless"

Client <-> Gatekeeper <-> Storage

The gatekeeper is essentially a list of identity-based ACL's for an object storage, and a method for identifying client identity.

It must be seeded with at least one existing identity, and whatever requirements a particular access control system would have.

## Gatekeeper

The gatekeeper must be "smart" enough to model whatever axioms for a particular access control system.

For example, a static list (possibly just one) of public keys could model the simplest access system of "identified -> all access", "not identified -> no access"

Making that list read from a storage object, would allow identities to grant new identities

From there, you can then add user and group style permissions (and therefore any access system on top of this)

(The limitation being that you cannot do "dynamic" access control. eg. time based access)
