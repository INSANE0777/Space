import spacex_agent
import weather_agent

def test_spacex_and_weather_agents():
    data = {}
    print("Starting test: SpaceX + Weather agents\n")

    # Run SpaceX agent
    print("Running SpaceX Agent...")
    data = spacex_agent.run(data)  # call the module's run function directly
    print("SpaceX Agent Output:")
    print(data.get("spacex"))
    print("-" * 50)

    # Check if coordinates are present before running weather agent
    coords = data.get("spacex", {}).get("coordinates")
    if not coords or not coords.get("latitude") or not coords.get("longitude"):
        print("⚠️ Coordinates missing from SpaceX data. Cannot run Weather Agent reliably.")
        print("Adding fallback coordinates for testing.")
        data.update({
            "latitude": 28.6081,
            "longitude": -80.6039,
            "location": "Kennedy Space Center"
        })

    # Run Weather agent
    print("Running Weather Agent...")
    data = weather_agent.run(data)  # call the module's run function directly
    print("Weather Agent Output:")
    print(data.get("weather"))
    print("-" * 50)

    print("Test completed. Full data:")
    print(data)

if __name__ == "__main__":
    test_spacex_and_weather_agents()
