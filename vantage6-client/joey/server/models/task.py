from sqlalchemy import Column, String, Text, ForeignKey, Integer, sql
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .node import Node
from .base import Base, Database
from .collaboration import Collaboration


class Task(Base):
    """Central definition of a single task.
    
    A task can assigned in the TaskAssignment for multiple organizations. The input
    of the task is different for each organization (due to the encryption). Therefore
    the input for the task is encrypted for each organization independently. 
    """

    # fields
    name = Column(String)
    description = Column(String)
    image = Column(String)
    collaboration_id = Column(Integer, ForeignKey("collaboration.id"))
    run_id = Column(Integer) 
    parent_id = Column(Integer, ForeignKey("task.id"))
    database = Column(String)

    # relationships
    collaboration = relationship("Collaboration", back_populates="tasks")
    parent = relationship("Task", remote_side="Task.id", backref="children")
    task_assignments = relationship("TaskAssignment", back_populates="task")

    @hybrid_property
    def complete(self):
        return all([r.result.complete for r in self.task_assignments])
    
    @hybrid_property
    def results(self):
        return [ta.result for ta in self.task_assignments]

    def results_for_node(self, node):
        assert isinstance(node, Node), "Should be a node..."
        return [ta.result for ta in self.task_assignments if \
            ta.task.collaboration==node.collaboration and \
            ta.organization==node.organization ]
    
    @classmethod
    def next_run_id(cls):
        session = Database().Session
        max_run_id = session.query(sql.func.max(cls.run_id)).scalar()
        if max_run_id:
            return max_run_id + 1
        else:
            return 1

    def __repr__(self):
        return (f"<Task "
            f"name:{self.name}, "
            f"collaboration:{self.collaboration.name}"
        ">")