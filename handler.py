# RunPod serverless handler for ComfyUI character generation.
# Initializes ComfyUICharacter at startup (not on first request) to avoid
# execution timeout — model loading happens during container startup phase.
import logging
import os
import sys

import runpod

# Ensure handler's directory is on the Python path so comfyui_character is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from comfyui_character import ComfyUICharacter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)


# Lazy init on first request — startup init was hitting the serverless
# startup timeout because loading 2 SDXL checkpoints takes ~7 min.
worker = None


def handler(job):
    global worker
    job_input = job["input"]

    if worker is None:
        logger.info("Lazy-initializing ComfyUICharacter (startup init failed)...")
        worker = ComfyUICharacter()
        logger.info("ComfyUICharacter ready (lazy init)")

    return worker.generate(job_input)


runpod.serverless.start({"handler": handler})
