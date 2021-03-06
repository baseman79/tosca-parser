#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import TypeNotProvidedError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.elements.statefulentitytype import StatefulEntityType

SECTIONS = (LIFECYCLE, CONFIGURE, LIFECYCLE_SHORTNAME,
            CONFIGURE_SHORTNAME, EXTENTIONS) = \
           ('tosca.interfaces.node.lifecycle.Standard',
            'tosca.interfaces.relationship.Configure',
            'Standard', 'Configure', '_extensions')

INTERFACEVALUE = (IMPLEMENTATION, INPUTS) = ('implementation', 'inputs')

INTERFACE_DEF_RESERVED_WORDS = ['type', 'inputs', 'derived_from', 'version',
                                'description']


class InterfacesDef(StatefulEntityType):
    '''TOSCA built-in interfaces type.'''

    def __init__(self, node_type, interfacetype,
                 node_template=None, name=None, value=None):
        self.ntype = node_type
        self.node_template = node_template
        self.type = interfacetype
        self.name = name
        self.value = value
        self.implementation = None
        self.inputs = None
        self.defs = {}
        if interfacetype == LIFECYCLE_SHORTNAME:
            interfacetype = LIFECYCLE
        if interfacetype == CONFIGURE_SHORTNAME:
            interfacetype = CONFIGURE
        if hasattr(self.ntype, 'interfaces') \
           and self.ntype.interfaces \
           and interfacetype in self.ntype.interfaces:
            if 'type' in self.ntype.interfaces[interfacetype]:
                interfacetype = self.ntype.interfaces[interfacetype]['type']
            else:
                # In case of interfaces, the type need not be defined on the interfaces
                # in the inherited types. So take the type from parent node iterface defn.
                ty = self.ntype.parent_type
                while True:
                    ty = ty.parent_type
                    found = False
                    if not ty:
                        ExceptionCollector.appendException(
                            TypeNotProvidedError(what=interfacetype))
                        break
                    for intf, defn in ty.interfaces.items():
                        if intf == interfacetype:
                            if 'type' in defn:
                                interfacetype = defn['type']
                                found = True
                                break
                    if found:
                        break

        if node_type:
            if self.node_template and self.node_template.custom_def \
               and interfacetype in self.node_template.custom_def:
                self.defs = self.node_template.custom_def[interfacetype]
            else:
                self.defs = self.TOSCA_DEF[interfacetype]
        if value:
            if isinstance(self.value, dict):
                for i, j in self.value.items():
                    if i == IMPLEMENTATION:
                        self.implementation = j
                    elif i == INPUTS:
                        self.inputs = j
                    else:
                        what = ('"interfaces" of template "%s"' %
                                self.node_template.name)
                        ExceptionCollector.appendException(
                            UnknownFieldError(what=what, field=i))
            else:
                self.implementation = value

    def __str__(self):
        return "type: {}, name: {}, value: {}". format(
            self.type, self.name, self.value)

    @property
    def lifecycle_ops(self):
        if self.defs:
            if self.type == LIFECYCLE:
                return self._ops()

    @property
    def configure_ops(self):
        if self.defs:
            if self.type == CONFIGURE:
                return self._ops()

    def _ops(self):
        ops = []
        for name in list(self.defs.keys()):
            ops.append(name)
        return ops
