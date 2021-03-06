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


from toscaparser.elements.portspectype import PortSpec
from toscaparser.elements.statefulentitytype import StatefulEntityType


class DataType(StatefulEntityType):
    '''TOSCA built-in and user defined complex data type.'''

    NETWORK_TYPES = ('PortDef', PortSpec.SHORTNAME,
                     'PortInfo', 'NetworkInfo',)

    def __init__(self, datatypename, custom_def=None):
        prefix = self.DATATYPE_PREFIX
        if datatypename in self.NETWORK_TYPES:
            prefix = self.DATATYPE_NETWORK_PREFIX
        super(DataType, self).__init__(datatypename,
                                       prefix,
                                       custom_def)
        self.custom_def = custom_def

    @property
    def parent_type(self):
        '''Return a datatype this datatype is derived from.'''
        ptype = self.derived_from(self.defs)
        if ptype:
            return DataType(ptype, self.custom_def)
        return None

    @property
    def value_type(self):
        '''Return 'type' section in the datatype schema.'''
        return self.entity_value(self.defs, 'type')

    def get_all_properties_objects(self):
        '''Return all properties objects defined in type and parent type.'''
        props_def = self.get_properties_def_objects()
        # Get the property names
        prop_names = [p.name for p in props_def]
        ptype = self.parent_type
        while ptype:
            props = ptype.get_properties_def_objects()
            if props:
                for p in props:
                    if p.name not in prop_names:
                        props_def.append(p)
                        prop_names.append(p.name)
            ptype = ptype.parent_type
        return props_def

    def get_all_properties(self):
        '''Return a dictionary of all property definition name-object pairs.'''
        return {prop.name: prop
                for prop in self.get_all_properties_objects()}

    def get_all_property_value(self, name):
        '''Return the value of a given property name.'''
        props_def = self.get_all_properties()
        if props_def and name in props_def.key():
            return props_def[name].value
