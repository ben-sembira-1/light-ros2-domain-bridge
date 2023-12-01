# Querying relevant topic data

## Idea

If we want to create some kind of a middleware that allows our subsystems to use ROS and communicate with each other using low link resources we need to be able to query data about a specific topic.

Data that needs to be queried Given a topic name:
- Type

QOS is legit to be defined in the middleware itself, because inside a subsystem the QOS does not matter, they are always in the same LAN without packet loss or maximal bandwidth.