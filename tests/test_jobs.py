import pytest
from src.models.player import Player
from src.services.job_service import JobService
from src.models.job import JobType
from src.core.events import EventBus, EventHandler

@pytest.fixture
def event_bus():
    return EventBus()

@pytest.fixture
def player():
    return Player("test_user")

@pytest.fixture
def job_service(event_bus):
    return JobService(event_bus=event_bus)

def test_generate_jobs(player, job_service):
    jobs = job_service.generate_jobs_for_player(player, count=3)
    assert len(jobs) == 3
    # Check persistence
    assert len(player.active_jobs) == 3
    assert player.active_jobs[0]["id"] == jobs[0].id

def test_complete_it_support_job(player, job_service):
    jobs = job_service.generate_jobs_for_player(player, count=20)

    # Find an IT Support job
    job = next((j for j in jobs if j.job_type == JobType.IT_SUPPORT), None)
    assert job is not None

    # Complete it with option 0
    result = job_service.complete_job(player, job.id, choice_index=0)

    assert result["success"] is True
    assert player.stats.experience > 0

    # Check if job is removed
    updated_jobs = job_service.get_player_jobs(player)
    assert not any(j.id == job.id for j in updated_jobs)

def test_complete_scripting_job(player, job_service):
    jobs = job_service.generate_jobs_for_player(player, count=10) # Generate more to ensure we get a scripting job

    # Find a Scripting job
    job = next((j for j in jobs if j.job_type == JobType.SCRIPTING), None)

    # If we didn't get one (random chance), skip
    if not job:
        return

    expected_output = job.script_expected_output

    # Fail first
    result = job_service.complete_job(player, job.id, script_output="Wrong output")
    assert result["success"] is False

    # Succeed
    result = job_service.complete_job(player, job.id, script_output=expected_output)
    assert result["success"] is True
    assert player.stats.credits > 0

    # Check if job is removed
    updated_jobs = job_service.get_player_jobs(player)
    assert not any(j.id == job.id for j in updated_jobs)

def test_difficulty_scaling(job_service):
    # Level 1
    weights_lvl1 = job_service._get_difficulty_weights(1)
    assert weights_lvl1[0] > weights_lvl1[2] # Easy > Hard

    # Level 10
    weights_lvl10 = job_service._get_difficulty_weights(10)
    assert weights_lvl10[2] > weights_lvl10[0] # Hard > Easy

class MockHandler(EventHandler):
    def __init__(self):
        self.received_events = []

    def handle(self, event):
        self.received_events.append(event)
        return True

def test_job_completion_event(player, job_service, event_bus):
    handler = MockHandler()
    event_bus.subscribe("job_completed", handler)

    jobs = job_service.generate_jobs_for_player(player, count=1)
    job = jobs[0]

    if job.job_type == JobType.IT_SUPPORT:
        job_service.complete_job(player, job.id, choice_index=0)
    else:
        job_service.complete_job(player, job.id, script_output=job.script_expected_output)

    assert len(handler.received_events) == 1
    assert handler.received_events[0].data["job_id"] == job.id
