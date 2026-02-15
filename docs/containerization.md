# Containerization

Containerization is resolved to solve one pain point in software engineering, and that is the difference in program behavior caused by the deviance in environment setup.

With containrization, software apps can be run in isolated user spaces called *container* in any cloud/non-cloud environment.


# Docker

Docker uses OS-level virualization to deliver software in packages called *containers*. Docker supports multi container application, in a sense that docker also supports running multiple containers at the same time being able to connect them.

# How to Write a Dockerfile

To write a docker file, we need to have a good grasp of its structure.

1. Base Image: Start with an existing OS or platform, like MacOS, Python, Node.js.
2. Setup: Create working directories and copy files into the image.
3. Dependencies: Run commands to install libraries by like `pip install` or `npm install`, in our case `uv sync`.
4. Commands: Tell Docker what commands to run when the container starts.

## Instructions

Below are most often used keywords.

1. `FROM <base-image>`: specifies basic runtimes of the program, like `python:3.10-alpine`.
2. `WORKDIR <path>`: sets the working directory for **subsequence commands**.


# References

- [https://learnxinyminutes.com/docker/][https://learnxinyminutes.com/docker/]
