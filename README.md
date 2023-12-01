# light-ros2-domain-bridge

**WIP**

light-ros2-domain-bridge is planned to be a bridge that connects multiple ros2 domains using a light and reliable protocol that is based on UDP.
For terminology, we will call a specific subsystem (or group) bridge end an **adapter** and the whole network of adapters the **bridge**

## Basic Needs

- Reliability:
	- Not Reliable: If the data did not manage to get to the destination, the system should not try sending it again. This kind of data will probably be sent later with updated values.
	- Reliable: If the data did not manage to get to the destination, the system should make all its efforts to send it again and again until all recipients will get the data. This kind of data should get delivered at all costs, and as fast as possible.
	- Relevant: Given a ttl, as long as the data did not expire the system should act as if it was a *Reliable* piece of data. After the expiration time (aka ttl) the data should be discarded.
- Security (For each adapter):
	- Groups: Support for groups where all data is available among its parts, but between groups only allowed data can travel.
	- Publicity: Support for exposing only specific endpoints to other adapters in the network.
	- Firewall: Support for importing only specific endpoints from other adapters in the network.
- CAP Theorem:
	- We want the system to be CP - consistent and partition tolerant. It is ok that when one node is down, some data will not be available.
- Reboot Tolerance
	- The system should keep working when one node is restarted.
	- QUESTION: How much do we want to be tolerant to this? What if more than one node crashes? Do we always need to keep going from the same state as we was before the crash? If we do, isn't it dangerous to get into a crash loop where the last state is problematic and makes the system to crash each time it tries to re-spawn itself?

## Usage

### Option 1

#### Deployment

Imagine a node that a programmer can insert to its project + a config file,
and from there based on the configurations only the exposed data can be accessed from other adapters.

Maybe deploying it as a standalone docker container that is running aside to the business logic nodes is a good idea.
Thinking about going the other way of a kind-of ROS package that all subsystems should use, and it feels much more complicated.

#### Configurations

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

### Option 2

#### Configurations

Imagine something similar to FastAPI that allows a programer do define API endpoints functions in a specific API python file.
something like:

```python
from ROSBridgeApi import Router, QOS
from APITypes import Telemetries, TurnOnCameraPayload  # Those are pydantic models
from PrivateTypes import ElectricStatus, HealthStatus, TurnOnCameraRequest

router = Router.create_router()

@router.publisher(
	public_topic_name='/telemetries',
	QOS=QOS(reliable=False, TTL=None)
	private_dependencies={
		"electrics_status": TopicDependency('/electrics'),
		"health_status": TopicDependency('/health')
	}
)
def telemetries(electrics_status: ElectricStatus, health_status: HealthStatus) -> Telemetries:
	CM_IN_METER = 100
	return Telemetries(
		voltage=electrics_status.volt,
		current=electrics_status.I,
		distance_meters=electrics_status.distance_cm * CM_IN_METER
		healthy=health_status
	)



@router.subscriber(
	private_topic_name='/requests/turn_on_camera'
	public_dependencies={
		"request": TopicDependency('/turn_on_camera')
	}
)
def turn_on_camera(request: TurnOnCameraPayload) -> TurnOnCameraRequest:
	LOW_LIGHT_SHUTTER_SPEED_MS = 500
	NORMAL_SHUTTER_SPEED_MS = 100

	SLOW_GIMBAL_SPEED = 10
	NORMAL_GIMBAL_SPEED = 20

	def weight_to_resolution_and_fps(weight_kbps: int):
		MINIMAL_FPS = 5
		MAXIMAL_RESOLUTION = (1024, 768)

		maximal_resolution_weight = weight_kb(maximal_resolution) * MINIMAL_FPS
		ratio = (maximal_resolution / weight_kbps)
		if (ratio > 1):
			import numpy
			return (tuple(numpy.array(MAXIMAL_RESOLUTION) // ratio), MINIMAL_FPS)
		else:
			return (MAXIMAL_RESOLUTION, MINIMAL_FPS // ratio)

	resolution, fps = weight_to_resolution_and_fps(request.maximal_downlink_kbps)

	return TurnOnCameraRequest(
		allow_gimbal = True
		shutter_speed_ms = LOW_LIGHT_SHUTTER_SPEED if request.low_light else NORMAL_SHUTTER_SPEED_MS,
		gimbal_speed_deg_per_second = SLOW_GIMBAL_SPEED if request.low_light else NORMAL_GIMBAL_SPEED,
		resolution = resolution
		fps = fps
		highlight_walls = request.highlight_walls
	)

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

URLS to check:
- [time-sensitive-networking-for-robotics](https://medium.com/hackernoon/time-sensitive-networking-for-robotics-6b43590fa923)
- [What-Are-The-Communication-Protocols-Used-In-Industrial-Robotics](https://blog.robotiq.com/bid/32559/What-Are-The-Communication-Protocols-Used-In-Industrial-Robotics)
- [industrial-protocols](https://www.clarify.io/learn/industrial-protocols)

