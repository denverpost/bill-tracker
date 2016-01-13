#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template class
import os
import doctest
import string
import argparse
from datetime import date, timedelta

class Template:
    """ A vanilla class for sticking data into markup.
        """

    def __init__(self, data, data_type=None):
        """ Initialize the object.
            """
        self.data = data
        self.limit = 0
        if data_type:
            self.data_type = data_type
            self.load_template()

    def set_slug(self, value):
        """ Set the object slug value.
            """
        self.slug = value
        return value

    def set_metadata(self, value):
        """ Set the object metadata dict.
            """
        self.metadata = value
        return value

    def set_data(self, value):
        """ Set the object data value.
            """
        self.data = value
        return value

    def set_data_type(self, value):
        """ Set the object data_type value.
            """
        self.data_type = value
        return value

    def read_file(self, fn):
        """ Read the contents of a file.
            """
        f = open(fn, 'rb')
        content = f.read()
        f.close()
        return content

    def load_template(self, data_type=None):
        """ Populates template var, the template depends on the data_type.
            """
        if not data_type:
            data_type = self.data_type

        path = 'html/%s.html' % data_type

        if os.path.isfile(path) == False:
            raise ValueError("Template file %s does not exist" % path)

        f = open(path, 'rb')
        self.template = f.read()
        return self.template

    def write_template(self):
        """ Edit the template var with the values from the data var.
            """
        # The template is loaded in the init method.
        if self.template == '':
            raise ValueError("template var must exist and be something.")
        output = self.template

        self.output = output
        return output

    def get_date(self, date_offset, date_format="%a."):
        """ Helper method for taking an integer (the integer being the offset
            from the current day, where 0 = today, 1 = tomorrow etc.), and
            returning a formatted date.
            Format defaults to abbreviated weekday: "Wed."
            """
        if date_offset == 0:
            return "Today"
        return date.strftime(date.today() + timedelta(date_offset), date_format)

    def write_file(self):
        """ Write the parsed contents of a template to a file.
            """
        self.slug = self.slug.replace('+', '_')
        self.slug = self.slug.replace(' ', '_')
        path = 'www/output/%s-%s.html' % ( self.data_type, self.slug )
        f = open(path, 'wb')
        f.write(self.output)
        f.close()
        return "Successfully written to %s" % path
