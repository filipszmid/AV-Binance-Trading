def test_graphics_service(graphics_service, example_named_data):
    graphics_service.plot_high_low(example_named_data)
    print(example_named_data)
    graphics_service.plot_line(65000)
    graphics_service.show()
