# light-ros2-domain-bridge

**WIP**

light-ros2-domain-bridge is planned to be a bridge that connects multiple ros2 domains using a light and reliable protocol that is based on UDP.
For terminology, we will call a specific subsystem bridge end an **adapter** and the whole network of adapters the **bridge**

## Basic Needs

- Support for sending 3 kinds of data:
	- Not Reliable: If the data did not manage to get to the destination, the system should not try sending it again. This kind of data will probably be sent later with updated values.
	- Reliable: If the data did not manage to get to the destination, the system should make all its efforts to send it again and again until all recipients will get the data. This kind of data should get delivered at all costs, and as fast as possible.
	- Relevant: Given a ttl, as long as the data did not expire the system should act as if it was a *Reliable* piece of data. After the expiration time (aka ttl) the data should be discarded.
- Support for exposing from an adapter only specific endpoints to other adapters in the network.

## Usage

### Deployment

Imagine a node that a programmer can insert to its project + a config file,
and from there based on the configurations only the exposed data can be accessed from other adapters.

Maybe deploying it as a standalone docker container that is running aside to the business logic nodes is a good idea.
Thinking about going the other way of a kind-of ROS package that all subsystems should use, and it feels much more complicated.

### Configurations

Point to think about - How will we propagate types?

Something like:
```json
{
	"pears": ["192.168.1.25", "192.168.1.39", "whatever_dns_name"],
	"outputs": {
		"topics": [
			{
				"endpoint": "/robot1/telemetries",
				"ttl_seconds": 0,
			},
			{
				"endpoint": "/robot1/errors",
				"ttl_seconds": null,
			},
			{
				"endpoint": "/robot2/go_home",
				"ttl_seconds": 5,
			},
		],
		"services": [],
	},
	"inputs": {
		"topics": ["~/go_home", "~/toggle_light"],
		"services": ["~/health_check"]
	},
}
```

## implementation

### Types

In some way the receiving adapter should know what is the ROS interface of the message and publish it in its domain.
- Is it possible to publish a message without a compiled already message object?
- Is it possible to create a ROS interface message on run-time
If the answer is "no" or "well you can, but.." on both questions -
we should probably start thinking about adding to the configuration file the interface message type name and make sure the adaptors have
access to the projects interfaces.

### Logs

It can be very useful if all adapters will save logs of all incoming and outgoing data. Very useful for later research.

### QOS Profiles
There are 2 options for implementing profiles:
1. The bridge will not give all QOS features that ros2 give, but only 3 basic profiles - BEST_EFFORT, RELIABLE, RELEVANT.
1. The bridge will give access to a TTL option in the configurations where:
	- null			means RELIABLE - do all you can to send to all your pears
	- 0 or less		means BEST_EFFORT - do not even try to send again
	- any>0			means RELEVANT - do all you can to send to all your pears until the given time has passed
1. The bridge will have plugins that defines new QOS profiles based on the ROS QOS profile of the data

### Getting the data in and out

We will probably need some kind of ros bridge from ROS2 to AsyncIO.

### The protocol to use between 2 adapters (bridges)

Options:
- Just simple UDP, Maybe the things we are doing are not that complicated and we can write it all ourself with good tests.
- RPL - seems that all the internet is flooded with this protocol when searching for a "lossy network protocol".
- WIP


