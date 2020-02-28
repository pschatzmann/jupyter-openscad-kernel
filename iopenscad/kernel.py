####
## Jupyter Kernel for OpenSCAD
##
import os
import base64
from iopenscad.parser import Parser
from ipykernel.kernelbase import Kernel

class IOpenSCAD(Kernel):
    banner = "OpenSCAD"
    implementation = 'ipopenscad'
    implementation_version = '1.0'
    language = 'openscad'  # will be used for syntax highlighting
    language_version = '3.6'
    language_info = {'name': 'OpenSCAD',
                     'mimetype': 'application/x-openscad',
                     'extension': '.scad'}
    complete = ["cube(size = [x,y,z], center = true);","sphere(r = 10);",
        "sphere(d = 20);","cylinder(h=15, r1=9.5, r2=19.5, center=true);",
        "square([10,10],center=true);","circle(r=10);","circle(d=20);",
        "translate([x,y,z])","rotate([x,y,z])","scale([x,y,z])","resize([x,y,z])","mirror([x,y,z])",
        "hull(){...};","minkowski(){...};",
        "union() {...};","difference(){...};","intersection(){...};",
        "include <file>","use <file>",
        "module name() { ... }","function name() = ... ;"
    ]
    parser = None
    isSetup = False

    ##
    # Executes the source code which is defined in a cell
    ##
    def do_execute(self, code, silent,
                   store_history=True,
                   user_expressions=None,
                   allow_stdin=False):

        # Setup parser
        if not self.parser:
            self.parser = Parser()
            self.parser.setup()

        resultObj = None
        self.parser.parse(code)
        
        if not silent:
            # We send the standard output to the
            # client.
            if "%display" in code:
                self.displayMessages(self.parser)
                self.parser.clearMessages()
                resultFile = self.parser.renderMime()
                if resultFile:
                    resultObj = open(resultFile,'rb').read()
                    if self.parser.mime=='text/plain':
                        resultObj = resultObj.decode('utf-8')
                    else:
                        resultObj = base64.standard_b64encode(resultObj).decode('utf-8')

                if self.parser.getMessages().strip():
                    self.displayMessages(self.parser)
                if resultObj:
                    self.displayImage(resultObj, self.parser.mime)
                else:
                    if self.parser.getSourceCode().strip():
                        self.displayError(os.linesep+self.parser.getSourceCode())
            else:
                self.displayMessages(self.parser)

        # We return the exection results.
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    ##
    # Determine completion result
    ##
    def do_complete(self, code, cursor_pos):
        char = code[cursor_pos]
        result = self.complete + self.parser.getModuleNames() + self.parser.lsCommands
        result.sort()

        # filter the result if necessary
        if char.strip():
            subset = []
            for cmd in result:
                if cmd.startswith(char):
                    subset.append(cmd)
            result = subset

        content = {
            # The list of all matches to the completion request, such as
            # ['a.isalnum', 'a.isalpha'] for the above example.
            'matches' : result,

            # The range of text that should be replaced by the above matches when a completion is accepted.
            # typically cursor_end is the same as cursor_pos in the request.
            'cursor_start' : cursor_pos,
            'cursor_end' : cursor_pos,

            # status should be 'ok' unless an exception was raised during the request,
            # in which case it should be 'error', along with the usual error message content
            # in other messages.
            'status' : 'ok'
        }
        return content

    ##
    # Cleanup
    ##
    def do_shutdown(self, restart):
        self.parser.close()

    def displayInfo(self, info):
        stream_content = {'name': 'stdout', 'text': info}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def displayError(self, error):
        stream_content = {'name': 'stderr', 'text': error}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def displayMessages(self, parser):
        if self.parser.isError:
            self.displayError(parser.getMessages())
        else:
            self.displayInfo(parser.getMessages())

    
    def displayImage(self, resultObj, mime):
        if resultObj:
            # We prepare the response with our rich
            # data (the plot).
            content = {
                'source': 'kernel',

                # This dictionary may contain
                # different MIME representations of
                # the output.
                'data': {
                    mime: resultObj
                },

                # We can specify the image size
                # in the metadata field.
                'metadata' : {
                    mime : {
                        'width': 600,
                        'height': 400
                    }
                }
            }

            # We send the display_data message with
            # the contents.
            self.send_response(self.iopub_socket, 'display_data', content)

