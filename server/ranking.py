from .extensions import driver, scheduler

@scheduler.task(
    trigger="interval",
    id="feedback",
    seconds=10,
    max_instances=1,
)
def learn_with_feedback():
    driver.learn_with_feedback()