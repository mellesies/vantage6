import jwt
import json as json_lib
import time

from typing import Any

from vantage6.common.client.client_base import ClientBase
from vantage6.common import base64s_to_bytes, bytes_to_base64s
from vantage6.common.task_status import has_task_finished
from vantage6.common.serialization import serialize
from vantage6.algorithm.tools.util import info


class AlgorithmClient(ClientBase):
    """
    Interface to communicate between the algorithm container and the central
    server via a local proxy server.

    An algorithm container cannot communicate directly to the
    central server as it has no internet connection. The algorithm can,
    however, talk to a local proxy server which has interface to the central
    server. This way we make sure that the algorithm container does not share
    details with others, and we also can encrypt the results for a specific
    receiver. Thus, this not a interface to the central server but to
    the local proxy server - however, the interface looks identical to make
    it easier to use.

    Parameters
    ----------
    token: str
        JWT (container) token, generated by the node the algorithm container
        runs on
    *args, **kwargs
        Arguments passed to the parent ClientBase class.
    """

    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # obtain the identity from the token
        jwt_payload = jwt.decode(
            token, options={"verify_signature": False})

        container_identity = jwt_payload['sub']

        self.image = container_identity.get("image")
        self.databases = container_identity.get('databases', [])
        self.node_id = container_identity.get("node_id")
        self.collaboration_id = container_identity.get("collaboration_id")
        self.organization_id = container_identity.get("organization_id")
        self.log.info(
            f"Container in collaboration_id={self.collaboration_id} \n"
            f"Key created by node_id {self.node_id} \n"
            f"Can only use image={self.image}"
        )

        # attach sub-clients
        self.run = self.Run(self)
        self.result = self.Result(self)
        self.task = self.Task(self)
        self.vpn = self.VPN(self)
        self.organization = self.Organization(self)
        self.collaboration = self.Collaboration(self)
        self.node = self.Node(self)

        self._access_token = token

    def request(self, *args, **kwargs) -> dict:
        """
        Make a request to the central server. This overwrites the parent
        function so that containers will not try to refresh their token, which
        they would be unable to do.

        Parameters
        ----------
        *args, **kwargs
            Arguments passed to the parent ClientBase.request function.

        Returns
        -------
        dict
            Response from the central server.
        """
        return super().request(*args, **kwargs, retry=False)

    def authenticate(self, credentials: dict = None, path: str = None) -> None:
        """
        Overwrite base authenticate function to prevent algorithm containers
        from trying to authenticate, which they would be unable to do (they are
        already provided with a token on container startup).

        Function parameters have only been included to make the interface
        identical to the parent class. They are not used.

        Parameters
        ----------
        credentials: dict
            Credentials to authenticate with.
        path: str
            Path to the credentials file.

        Raises
        ------
        NotImplementedError
            Always.
        """
        return NotImplementedError("Algorithm containers cannot authenticate!")

    def refresh_token(self) -> None:
        """
        Overwrite base refresh_token function to prevent algorithm containers
        from trying to refresh their token, which they would be unable to do.

        Raises
        ------
        NotImplementedError
            Always.
        """
        return NotImplementedError(
            "Algorithm containers cannot refresh their token!")

    def wait_for_results(self, task_id: int, interval: float = 1) -> list:
        """
        Poll the central server until results are available and then return
        them.

        Parameters
        ----------
        task_id: int
            ID of the task for which the results should be obtained.
        interval: float
            Interval in seconds to wait between checking server for results.

        Returns
        -------
        list
            List of task results.
        """
        status = self.task.get(task_id).get('status')
        while not has_task_finished(status):
            info(f"Waiting for results of task {task_id}...")
            time.sleep(interval)
            status = self.task.get(task_id).get('status')
        info("Done!")

        return self.result.from_task(task_id)

    def _multi_page_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Make multiple requests to the central server to get all pages of a list
        of results.

        Parameters
        ----------
        endpoint: str
            Endpoint to which the request should be made.
        params: dict
            Parameters to be passed to the request.

        Returns
        -------
        dict
            Response from the central server.
        """
        if params is None:
            params = {}
        # get first page
        page = 1
        params["page"] = page
        response = self.request(endpoint, params=params)

        # append next pages (if any)
        links = response.get("links")
        while links and links.get("next"):
            page += 1
            params["page"] = page
            response["data"] += self.request(endpoint, params=params)["data"]
            links = response.get("links")

        return response['data']

    class Run(ClientBase.SubClient):
        """
        Algorithm Run client for the algorithm container.

        This client is used to obtain algorithm runs of tasks with the same
        job_id from the central server.
        """

        def get(self, id_) -> dict:
            """
            Obtain a specific algorithm run from the central server.

            Parameters
            ----------
            id_: int
                ID of the algorithm run that should be obtained.

            Returns
            -------
            dict
                Algorithm run data.
            """
            return self.parent.request(f"run/{id_}")

        def from_task(self, task_id: int) -> list:
            """
            Obtain algorithm runs from a specific task at the server.

            Containers are allowed to obtain the runs of their children
            (having the same job_id at the server). The permissions are checked
            at te central server.

            Note that the returned results are not decrypted. The algorithm is
            responsible for decrypting the results.

            Parameters
            ----------
            task_id: int
                ID of the task from which you want to obtain the algorithm runs

            Returns
            -------
            list
                List of algorithm run data. The type of the results depends on
                the algorithm.
            """
            # TODO do we need this function? It may be used to collect data
            # on subtasks but usually only the results are accessed, which is
            # done with the function below.
            return self.parent._multi_page_request(
                "run", params={"task_id": task_id}
            )

    class Result(ClientBase.SubClient):
        """
        Result client for the algorithm container.

        This client is used to get results from the central server.
        """
        def get(self, id_: int) -> Any:
            """
            Obtain a specific result from the central server.

            Parameters
            ----------
            id_: int
                ID of the algorithm run of which the result should be obtained.

            Returns
            -------
            Any
                Result of the algorithm run.
            """
            response = self.parent.request(f"result/{id_}")

            # Encryption is not done at the client level for the container. The
            # algorithm developer is responsible for decrypting the results.
            self.parent.log.info('--> Attempting to decode results!')
            result = None
            if response.get('result'):
                result = json_lib.loads(
                    base64s_to_bytes(response.get('result')).decode()
                )
            return result

        def from_task(self, task_id: int) -> list[Any]:
            """
            Obtain results from a specific task at the server.

            Containers are allowed to obtain the results of their children
            (having the same job_id at the server). The permissions are checked
            at te central server.

            Results are decrypted by the proxy server and decoded here before
            returning them to the algorithm.

            Parameters
            ----------
            task_id: int
                ID of the task from which you want to obtain the results

            Returns
            -------
            list[Any]
                List of results. The type of the results depends on the
                algorithm.
            """
            results = self.parent._multi_page_request(
                "result", params={"task_id": task_id}
            )

            # Encryption is not done at the client level for the container. The
            # algorithm developer is responsible for decrypting the results.
            decoded_results = []
            try:
                decoded_results = [
                    json_lib.loads(
                        base64s_to_bytes(result.get("result")).decode()
                    )
                    for result in results if result.get("result")
                ]
            except Exception as e:
                self.parent.log.error('Unable to load results')
                self.parent.log.debug(e)

            return decoded_results

    class Task(ClientBase.SubClient):
        """
        A task client for the algorithm container.

        It provides functions to get task information and create new tasks.
        """
        def get(self, task_id: int) -> dict:
            """
            Retrieve a task at the central server.

            Parameters
            ----------
            task_id : int
                ID of the task to retrieve

            Returns
            -------
            dict
                Dictionary containing the task information
            """
            return self.parent.request(
                f"task/{task_id}"
            )

        def create(
            self, input_: bytes, organizations: list[int] = None,
            name: str = "subtask", description: str = None
        ) -> dict:
            """
            Create a new (child) task at the central server.

            Containers are allowed to create child tasks (having the
            same job_id) at the central server. The docker image must
            be the same as the docker image of this container self.

            Parameters
            ----------
            input_ : bytes
                Input to the task. Should be b64 encoded.
            organizations : list[int]
                List of organization IDs that should execute the task.
            name: str, optional
                Name of the subtask
            description : str, optional
                Description of the subtask

            Returns
            -------
            dict
                Dictionary containing information on the created task
            """
            if not organizations:
                organizations = []
            self.parent.log.debug(f"Creating new subtask for {organizations}")

            description = (
                description or
                f"task from container on node_id={self.parent.node_id}"
            )

            # serializing input. Note that the input is not encrypted here, but
            # in the proxy server (self.parent.request())
            serialized_input = bytes_to_base64s(serialize(input_))
            organization_json_list = []
            for org_id in organizations:
                organization_json_list.append(
                    {
                        "id": org_id,
                        "input": serialized_input
                    }
                )

            return self.parent.request('task', method='post', json={
                "name": name,
                "image": self.parent.image,
                "collaboration_id": self.parent.collaboration_id,
                "description": description,
                "organizations": organization_json_list,
                "databases": self.parent.databases
            })

    class VPN(ClientBase.SubClient):
        """
        A VPN client for the algorithm container.

        It provides functions to obtain the IP addresses of other containers.
        """
        def get_addresses(
            self, only_children: bool = False, only_parent: bool = False,
            only_siblings: bool = False, only_self: bool = False,
            include_children: bool = False, include_parent: bool = False,
            label: str = None
        ) -> list[dict]:
            """
            Get information about the VPN IP addresses and ports of other
            algorithm containers involved in the current task. These addresses
            can be used to send VPN communication to.

            Multiple ports may be exposed for a single algorithm run, so it
            is possible that multiple ports are returned for a single IP.

            Parameters
            ----------
            only_children : bool, optional
                Only return the IP addresses of the children of the current
                task, by default False. Incompatible with other only_*
                parameters.
            only_parent : bool, optional
                Only return the IP address of the parent of the current task,
                by default False. Incompatible with other only_*
                parameters.
            only_siblings: bool, optional
                Only return the IP addresses of the siblings of the current
                task, by default False. Incompatible with other only_*
                parameters.
            only_self: bool, optional
                Only return the IP address of the current task, by default
                False. Incompatible with other only_* parameters.
            include_children : bool, optional
                Include the IP addresses of the children of the current task,
                by default False. Incompatible with only_parent, superseded
                by only_children.
            include_parent : bool, optional
                Include the IP address of the parent of the current task, by
                default False. Incompatible with only_children, superseded by
                only_parent.
            label : str, optional
                The label of the port you are interested in, which is set
                in the algorithm Dockerfile. If this parameter is set, only
                the ports with this label will be returned.

            Returns
            -------
            list[dict]
                List of dictionaries with algorithm addresses. Each dictionary
                contains the keys 'ip', 'port', 'label', 'organization_id',
                'task_id', and 'parent_id'. If obtaining the VPN addresses from
                the server fails, a dictionary with a 'message' key is returned
                instead.
            """
            # Only pass the parameters if they are not the default value - this
            # prevents that they are interpreted as string, which goes wrong
            # for 'False' or 'None' values in the proxy server
            params = {}
            if only_children:
                params['only_children'] = 1
            if only_parent:
                params['only_parent'] = 1
            if only_siblings:
                params['only_siblings'] = 1
            if only_self:
                params['only_self'] = 1
            if include_children:
                params['include_children'] = 1
            if include_parent:
                params['include_parent'] = 1
            if label:
                params['label'] = label

            results = self.parent.request(
                "vpn/algorithm/addresses", params=params
            )

            if 'addresses' not in results:
                return {'message': 'Obtaining VPN addresses failed!'}

            return results['addresses']

        # FIXME consider renaming this and similar functions in v5+: users
        # reported they expected a '{ip}:{port}' string, not a dict - we should
        # evaluate what is most effective though complete
        def get_parent_address(self) -> dict:
            """
            Get the IP address and port number of the parent of the current
            algorithm run.

            Multiple ports may be exposed for a single algorithm run, so it
            is possible that multiple ports are returned for a single IP.

            Returns
            -------
            list[dict]
                List of dictionaries with algorithm addresses. Each dictionary
                contains the keys 'ip', 'port', 'label', 'organization_id',
                'task_id', and 'parent_id'. If obtaining the VPN addresses from
                the server fails, a dictionary with a 'message' key is returned
                instead.
            """
            return self.get_addresses(only_parent=True)

        def get_child_addresses(self) -> list[dict]:
            """
            Get the IP addresses and port numbers of the children of the
            current algorithm run.

            Multiple ports may be exposed for a single algorithm run, so it
            is possible that multiple ports are returned for a single IP.

            Returns
            -------
            list[dict]
                List of dictionaries with algorithm addresses. Each dictionary
                contains the keys 'ip', 'port', 'label', 'organization_id',
                'task_id', and 'parent_id'. If obtaining the VPN addresses from
                the server fails, a dictionary with a 'message' key is returned
                instead.
            """
            return self.get_addresses(only_children=True)

        def get_sibling_addresses(self) -> list[dict]:
            """
            Get the IP addresses and port numbers of the siblings of the
            current algorithm run.

            Multiple ports may be exposed for a single algorithm run, so it
            is possible that multiple ports are returned for a single IP.

            Returns
            -------
            list[dict]
                List of dictionaries with algorithm addresses. Each dictionary
                contains the keys 'ip', 'port', 'label', 'organization_id',
                'task_id', and 'parent_id'. If obtaining the VPN addresses from
                the server fails, a dictionary with a 'message' key is returned
                instead.
            """
            return self.get_addresses(only_siblings=True)

        def get_own_address(self) -> dict:
            """
            Get the IP address and port number of the current algorithm run.

            Multiple ports may be exposed for a single algorithm run, so it
            is possible that multiple ports are returned for a single IP.

            Returns
            -------
            list[dict]
                List of dictionaries with algorithm addresses. Each dictionary
                contains the keys 'ip', 'port', 'label', 'organization_id',
                'task_id', and 'parent_id'. If obtaining the VPN addresses from
                the server fails, a dictionary with a 'message' key is returned
                instead.
            """
            return self.get_addresses(only_self=True)

    class Organization(ClientBase.SubClient):
        """
        Get information about organizations in the collaboration.
        """
        def get(self, id_: int) -> dict:
            """
            Get an organization by ID.

            Parameters
            ----------
            id: int
                ID of the organization to retrieve

            Returns
            -------
            dict
                Dictionary containing the organization data.
            """
            return self.parent.request(f"organization/{id_}")

        def list(self) -> list[dict]:
            """
            Obtain all organization in the collaboration.

            The container runs in a Node which is part of a single
            collaboration. This method retrieves all organization data that are
            within that collaboration. This can be used to target specific
            organizations in a collaboration.

            Returns
            -------
            list[dict]
                List of organizations in the collaboration.
            """
            return self.parent._multi_page_request(
                endpoint="organization", params={
                    "collaboration_id": self.parent.collaboration_id
                }
            )

    class Collaboration(ClientBase.SubClient):
        """
        Get information about the collaboration.
        """
        def get(self) -> dict:
            """
            Get the collaboration data.

            Returns
            -------
            dict
                Dictionary containing the collaboration data.
            """
            return self.parent.request(
                f"collaboration/{self.parent.collaboration_id}")

    class Node(ClientBase.SubClient):
        """
        Get information about the node.
        """
        def get(self) -> dict:
            """
            Get the node data.

            Returns
            -------
            dict
                Dictionary containing data on the node this algorithm is
                running on.
            """
            return self.parent.request(f"node/{self.parent.node_id}")
