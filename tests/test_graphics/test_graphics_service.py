def test_graphics_service(graphics_service_fixture, example_named_data):
    graphics_service_fixture.plot_high_low(example_named_data)
    print(example_named_data)
    graphics_service_fixture.plot_line(65000)
    graphics_service_fixture.show()
