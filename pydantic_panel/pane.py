
import pydantic
import param
from panel.io import init_doc, state
from panel.layout import (
    Column, Panel, Row, Spacer, Tabs,
)
from panel.pane import PaneBase
from .widgets import PydanticModelEditor

from typing import (
    TYPE_CHECKING, Any, ClassVar, List, Mapping, Optional,
)


# if TYPE_CHECKING:
from bokeh.document import Document
from bokeh.model import Model
from pyviz_comms import Comm


class Pydantic(PaneBase):
    default_layout = param.ClassSelector(default=Column, class_=Panel,
                                         is_instance=False)
    object = param.Parameter()

    def __init__(self, object=None, **params):

        if isinstance(object, pydantic.BaseModel):
            self.widget = PydanticModelEditor(value=object)
            self.object = object

        elif issubclass(object, pydantic.BaseModel):
            self.widget = PydanticModelEditor(class_=object)
            self.widget.link(self, value='object')
        else:
            raise
        self.layout = self.default_layout(self.widget)
        

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = self.layout._get_model(doc, root, parent, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _cleanup(self, root: Optional[Model] = None) -> None:
        self.layout._cleanup(root)
        super()._cleanup(root)

    @classmethod
    def applies(cls, obj: Any, **params) -> Optional[bool]:
        if isinstance(obj, pydantic.BaseModel):
            return True
        if issubclass(obj, pydantic.BaseModel):
            return True
            
    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Arguments
        ---------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        return super().select(selector) + self.layout.select(selector)

    def get_root(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
        preprocess: bool = True
    ) -> Model:
        """
        Returns the root model and applies pre-processing hooks

        Arguments
        ---------
        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        preprocess: boolean (default=True)
          Whether to run preprocessing hooks

        Returns
        -------
        Returns the bokeh model corresponding to this panel object
        """
        doc = init_doc(doc)
        root = self.layout.get_root(doc, comm, preprocess)
        ref = root.ref['id']
        self._models[ref] = (root, None)
        state._views[ref] = (self, root, doc, comm)
        return root
