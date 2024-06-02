from reinforcement_learning.training_config import main_config, create_config

if __name__ == "__main__":
    from ding.entry import serial_pipeline
    serial_pipeline([main_config, create_config], seed=21, max_env_step=int(1e8))