from .extensions import driver, scheduler

#TODO: Put correct time
@scheduler.task(
    trigger="interval",
    id="feedback",
    seconds=10,
    max_instances=1,
)
def learn_with_feedback():
    driver.learn_with_feedback()