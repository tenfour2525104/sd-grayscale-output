import launch
if not launch.is_installed("numpy"):
    launch.run_pip("install numpy", "numpy for grayscale-output")
