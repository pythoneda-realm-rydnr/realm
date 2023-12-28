"""
pythoneda/realm/rydnr/rydnr.py

This file declares the Rydnr class.

Copyright (C) 2023-today rydnr's pythoneda-realm-rydnr/realm

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from pythoneda import attribute, listen, sensitive, Event, EventEmitter, EventListener, Ports
from pythoneda.realm.rydnr.events import ChangeStagingCodeRequestDelegated
from pythoneda.shared.artifact_changes import Change
from pythoneda.shared.artifact_changes.events import (
    ChangeStagingCodeExecutionRequested, ChangeStagingCodePackaged, ChangeStagingCodeRequested
)
from pythoneda.shared.code_requests import CodeExecutionRequest
from pythoneda.shared.git import GitDiff, GitRepo


class Rydnr(EventListener):
    """
    Represents Rydnr.

    Class name: Rydnr

    Responsibilities:
        - Does whatever Rydnr can do in the PythonEDA ecosystem.

    Collaborators:
        - Potentially, any PythonEDA domain.
    """

    _singleton = None

    def __init__(self):
        """
        Creates a new Rydnr instance.
        """
        super().__init__()

    @classmethod
    def instance(cls):
        """
        Retrieves the singleton instance.
        :return: Such instance.
        :rtype: pythoneda.realm.rydnr.Rydnr
        """
        if cls._singleton is None:
            cls._singleton = cls.initialize()

        return cls._singleton

    @classmethod
    @listen(ChangeStagingCodeRequestDelegated)
    async def listen_ChangeStagingCodeRequestDelegated(cls, event: ChangeStagingCodeRequestDelegated) -> ChangeStagingCodeRequested:
        """
        Gets notified of a ChangeStagingCodeRequestDelegated event.
        Emits a ChangeStagingCodeRequested event.
        :param event: The event.
        :type event: pythoneda.realm.rydnr.events.ChangeStagingCodeRequestDelegated
        :return: A request to stage changes.
        :rtype: pythoneda.shared.artifact_changes.events.ChangeStagingCodeRequested
        """
        Rydnr.logger().debug(f"Received {type(event)}")
        repository_url = GitRepo.remote_urls(event.repository_folder)['origin'][0]
        branch = GitRepo.current_branch(event.repository_folder)
        # retrieve changes from the cloned repository.
        change = Change.from_unidiff_text(GitDiff(event.repository_folder).diff(), repository_url, branch, event.repository_folder)
        result = ChangeStagingCodeRequested(change, event.id)
        Rydnr.logger().debug(f"Emitting {type(result)}")
        await Ports.instance().resolve(EventEmitter).emit(result)
        return result

    @classmethod
    @listen(ChangeStagingCodePackaged)
    async def listen_ChangeStagingCodePackaged(cls, event: ChangeStagingCodePackaged):
        """
        Gets notified of a ChangeStagingCodePackaged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ChangeStagingCodePackaged
        """
        Rydnr.logger().debug(f"Received {type(event)}")
        # TODO: Implement a way to choose whether the code should be reviewed or executed
        await cls.request_execution(event)

    @classmethod
    async def request_execution(cls, event: ChangeStagingCodePackaged):
        """
        Requests the automated execution of the code upon receiving a ChangeStagingCodePackaged.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ChangeStagingCodePackaged
        """
        result = ChangeStagingCodeExecutionRequested(CodeExecutionRequest(event.nix_flake.code_request), event.id)
        Rydnr.logger().debug(f"Emitting {type(result)}")
        await Ports.instance().resolve(EventEmitter).emit(result)
        return result

    @classmethod
    async def launch_Jupyter(cls, event: ChangeStagingCodePackaged):
        """
        Launches Jupyterlab upon receiving a ChangeStagingCodePackaged.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ChangeStagingCodePackaged
        """
        Rydnr.logger().info(f"Running {type(event)}")
        await event.nix_flake.run()
