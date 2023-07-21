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
import logging
from pythoneda.value_object import attribute, sensitive
from pythoneda.event import Event
from pythoneda.event_emitter import EventEmitter
from pythoneda.event_listener import EventListener
from pythoneda.ports import Ports
from pythoneda.realm.rydnr.events.commit_change_delegated import CommitChangeDelegated
from pythoneda.shared.artifact_changes.events.commit_change_requested import CommitChangeRequested
from pythoneda.shared.git.git_repo import GitRepo
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
        :rtype: PythonEDA
        """
        if cls._singleton is None:
            cls._singleton = cls.initialize()

        return cls._singleton

    @classmethod
    def supported_events(cls) -> List[Type[Event]]:
        """
        Retrieves the list of supported event classes.
        :return: Such list.
        :rtype: List
        """
        return [ CommitChangeDelegated ]

    @classmethod
    async def listen_CommitChangeDelegated(cls, event: CommitChangeDelegated):
        """
        Gets notified of a CommitChangeDelegated event.
        Emits a CommitChangeRequested event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.commit_change_requested.CommitChangeRequested
        """
        event_emitter = Ports.instance().resolve(EventEmitter)
        repository_url = GitRepo.remote_urls(event.repository_folder)['origin'][0]
        branch = GitRepo.current_branch(event.repository_folder)
        await event_emitter.emit(CommitChangeRequested(repository_url, branch, event.id))
