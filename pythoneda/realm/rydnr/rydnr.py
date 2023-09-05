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
from pythoneda.shared.artifact_changes.events import ChangeStagingCodeRequested
from pythoneda.shared.artifact_changes.events import ChangeStagingCodeDescribed
from pythoneda.shared.git import GitDiff, GitRepo
from typing import List, Type

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
        event_emitter = Ports.instance().resolve(EventEmitter)
        repository_url = GitRepo.remote_urls(event.repository_folder)['origin'][0]
        branch = GitRepo.current_branch(event.repository_folder)
        # retrieve changes from the cloned repository.
        change = Change.from_unidiff_text(GitDiff(event.repository_folder).diff(), repository_url, branch, event.repository_folder)
        result = ChangeStagingCodeRequested(change, event.id)
        Rydnr.logger().debug(f"Emitting {type(result)}")
        await event_emitter.emit(result)
        return result

    @classmethod
    @listen(ChangeStagingCodeDescribed)
    async def listen_ChangeStagingCodeDescribed(cls, event: ChangeStagingCodeDescribed):
        """
        Gets notified of a ChangeStagingCodeDescribed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ChangeStagingCodeDescribed
        """
        Rydnr.logger().debug(f"Received {type(event)}")
        await event.code_request.run()
