import argparse
import random
import time

import paho.mqtt.client as mqtt


def build_payload(
    cycle_id: int,
    relay_id: int,
    runner_id: int,
    latitude: float,
    longitude: float,
    seq: int,
) -> str:
    pace = round(random.uniform(4.8, 6.4), 2)
    battery = max(1, 95 - seq)
    rssi = random.randint(-98, -72)
    snr = round(random.uniform(5.0, 10.0), 2)
    return (
        f"FORWARD,{cycle_id},{relay_id},{runner_id},"
        f"{latitude:.6f},{longitude:.6f},{pace},{battery},{seq},{rssi},{snr}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish fake runner locations to MQTT.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="marathon/gateways/gateway-1/data")
    parser.add_argument(
        "--runner-ids",
        default="7,8,9",
        help="Comma-separated runner ids, for example: 7,8,9",
    )
    parser.add_argument("--relay-id", type=int, default=1)
    parser.add_argument("--cycle-id", type=int, default=1)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--lat", type=float, default=36.10321)
    parser.add_argument("--lng", type=float, default=129.38712)
    args = parser.parse_args()

    runner_ids = parse_runner_ids(args.runner_ids)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, 60)
    client.loop_start()

    try:
        for seq in range(1, args.count + 1):
            for index, runner_id in enumerate(runner_ids):
                latitude = args.lat + (index * 0.00035) + (seq * 0.00005)
                longitude = args.lng + (index * 0.00030) + (seq * 0.00005)
                payload = build_payload(
                    args.cycle_id,
                    args.relay_id,
                    runner_id,
                    latitude,
                    longitude,
                    seq,
                )
                result = client.publish(args.topic, payload)
                result.wait_for_publish()
                print(f"published -> {args.topic}: {payload}")
            time.sleep(args.interval)
    finally:
        client.loop_stop()
        client.disconnect()


def parse_runner_ids(value: str) -> list[int]:
    runner_ids: list[int] = []
    for raw_runner_id in value.split(","):
        raw_runner_id = raw_runner_id.strip()
        if not raw_runner_id:
            continue
        runner_ids.append(int(raw_runner_id))

    if not runner_ids:
        raise ValueError("--runner-ids must contain at least one runner id")

    return runner_ids


if __name__ == "__main__":
    main()
