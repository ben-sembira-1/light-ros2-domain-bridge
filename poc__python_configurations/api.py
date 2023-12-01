from ROSBridgeApi import Router, QOS, TopicDependency
from APITypes import Telemetries, TurnOnCameraPayload  # Those are pydantic models
from PrivateTypes import ElectricStatus, HealthStatus, TurnOnCameraRequest

router = Router.create_router()


@router.publisher(
    public_topic_name="/telemetries",
    QOS=QOS(reliable=False, TTL=None),
    private_dependencies={
        "electrics_status": TopicDependency("/electrics"),
        "health_status": TopicDependency("/health"),
    },
)
def telemetries(
    electrics_status: ElectricStatus, health_status: HealthStatus
) -> Telemetries:
    CM_IN_METER = 100
    return Telemetries(
        voltage=electrics_status.volt,
        current=electrics_status.I,
        distance_meters=electrics_status.distance_cm * CM_IN_METER,
        healthy=health_status,
    )


@router.subscriber(
    private_topic_name="/requests/turn_on_camera",
    public_dependencies={"request": TopicDependency("/turn_on_camera")},
)
def turn_on_camera(request: TurnOnCameraPayload) -> TurnOnCameraRequest:
    LOW_LIGHT_SHUTTER_SPEED_MS = 500
    NORMAL_SHUTTER_SPEED_MS = 100
    SLOW_GIMBAL_SPEED = 10
    NORMAL_GIMBAL_SPEED = 20

    def weight_kb(resolution: tuple[int, int]) -> float:
        BYTES_IN_PIXEL = 4
        BYTES_IN_HEADER = 80
        BYTES_IN_KB = 1024

        weight_in_bytes = (
            resolution[0] * resolution[1] * BYTES_IN_PIXEL + BYTES_IN_HEADER
        )

        return weight_in_bytes // BYTES_IN_KB + 1

    def weight_to_resolution_and_fps(weight_kbps: int):
        MINIMAL_FPS = 5
        MAXIMAL_RESOLUTION = (1024, 768)

        maximal_resolution_weight = weight_kb(MAXIMAL_RESOLUTION) * MINIMAL_FPS
        ratio = maximal_resolution_weight / weight_kbps
        if ratio > 1:
            import numpy

            return (tuple(numpy.array(MAXIMAL_RESOLUTION) // ratio), MINIMAL_FPS)
        else:
            return (MAXIMAL_RESOLUTION, MINIMAL_FPS // ratio)

    resolution, fps = weight_to_resolution_and_fps(request.maximal_downlink_kbps)

    return TurnOnCameraRequest(
        allow_gimbal=True,
        shutter_speed_ms=LOW_LIGHT_SHUTTER_SPEED_MS
        if request.low_light
        else NORMAL_SHUTTER_SPEED_MS,
        gimbal_speed_deg_per_second=SLOW_GIMBAL_SPEED
        if request.low_light
        else NORMAL_GIMBAL_SPEED,
        resolution=resolution,
        fps=fps,
        highlight_walls=request.highlight_walls,
    )
