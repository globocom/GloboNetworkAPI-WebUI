# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import commands
import logging


class GITError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        msg = u"%s" % (self.error)
        return msg.encode("utf-8", "replace")


class GITCommandError(GITError):

    def __init__(self, error):
        GITError.__init__(self, error)

logger = logging.getLogger(__name__)

class Git():
    @classmethod
    def remove(cls, archive):
        '''Execute command remove in git

        :param archive: file to be remove 

        :raise GITCommandError: Failed to execute command
        '''
        try:
            (status, output) = commands.getstatusoutput("git rm %s" % archive)

        except Exception, e:
            (status, output) = (1, e)

        finally:

            if (status):
                msg = "GIT error: remove the file %s: %s" % (archive, output)
                logger.error(msg)
                raise GITCommandError(msg)

    @classmethod
    def add(cls, archive):
        '''Execute command add in git

        :param archive: file to be add 

        :raise GITCommandError: Failed to execute command
        '''
        try:
            (status, output) = commands.getstatusoutput("git add %s" % archive)

        except Exception, e:
            (status, output) = (1, e)

        finally:

            if (status):
                msg = "GIT error: add the file %s: %s" % (archive, output)
                logger.error(msg)
                raise GITCommandError(msg)

    @classmethod
    def commit(cls, archive, comment):
        '''Execute command commit in git

        :param archive: file to be committed
        :param comment: comments

        :raise GITCommandError: Failed to execute command
        '''
        try:
            (status, output) = commands.getstatusoutput("git commit -m '%s' %s" % (comment, archive))

        except Exception, e:
            (status, output) = (1, e)

        finally:

            if (status):
                msg = "GIT error: commit the file %s: %s" % (archive, output)
                logger.error(msg)
                raise GITCommandError(msg)

    @classmethod
    def push(cls):
        '''Execute command push in git

        :param archive: file to be committed
        :param comment: comments

        :raise GITCommandError: Failed to execute command
        '''
        try:
            (status, output) = commands.getstatusoutput("git push")

        except Exception, e:
            (status, output) = (1, e)

        finally:

            if (status):
                msg = "GIT error: push git: %s" % output
                logger.error(msg)
                raise GITCommandError(msg)

    @classmethod
    def synchronization(cls):
        '''Execute command update in git

        :raise GITCommandError: Failed to execute command
        '''
        try:
            (status, output) = commands.getstatusoutput("git pull")

        except Exception, e:
            (status, output) = (1, e)

        finally:

            if (status):
                msg = "GIT error: pull git: %s" % output
                logger.error(msg)
                raise GITCommandError(msg)
