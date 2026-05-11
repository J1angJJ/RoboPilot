## Summary

Describe the change and why it is needed.

## Type of Change

- [ ] Bug fix
- [ ] Documentation
- [ ] Packaging / release engineering
- [ ] Test update
- [ ] Feature work

## Safety Checklist

- [ ] This keeps RoboPilot no-ROS-required by default.
- [ ] This does not execute launch files, generated nodes, catkin, or colcon.
- [ ] File-writing behavior is explicit and safe.
- [ ] No API keys, tokens, `.env` files, `.pypirc`, or secrets are included.
- [ ] Documentation was updated if behavior or usage changed.

## Testing

Commands run:

```bash
python -m pytest
```

Windows fallback if used:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```
