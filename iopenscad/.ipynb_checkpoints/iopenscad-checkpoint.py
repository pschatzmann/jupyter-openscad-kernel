from ipykernel.kernelbase import Kernel
from parser import Parser
from parser import MimeConverter

####
## Jupyter Kernel for OpenSCAD
##
class IOpenSCAD(Kernel):
    banner = "OpenSCAD"
    implementation = 'ipopenscad'
    implementation_version = '1.0'
    language = 'openscad'  # will be used for syntax highlighting
    language_version = '3.6'
    language_info = {'name': 'OpenSCAD',
                     'mimetype': 'application/x-openscad',
                     'extension': '.scad'}
    parser = Parser()
    mime = "model/stl"
    complete = ["cube(size = [x,y,z], center = true);","sphere(r = 10);"
        "sphere(d = 20);","cylinder(h=15, r1=9.5, r2=19.5, center=true);"
        "square([10,10],center=true);","circle(r=10);","circle(d=20);",
        "translate([x,y,z])","rotate([x,y,z])","scale([x,y,z])","resize([x,y,z])","mirror([x,y,z])"
        "hull(){...};","minkowski(){...};"
        "union() {...};","difference(){...};","intersection(){...};"
        "include <file>","use <file>"
        "moduel name() { ... }","function name() = ... ;"
    ]

    ##
    # Executes the source code which is defined in a cell
    ##
    def do_execute(self, code, silent,
                   store_history=True,
                   user_expressions=None,
                   allow_stdin=False):

        resultObj = None
        self.parser.parse(code)
        resultFile = self.parser.renderMime()
        if resultFile:
            resultObj = open(resultFile,'rb').read()
        
        
        if not silent:
            # We send the standard output to the
            # client.
            self.send_response(
                self.iopub_socket,
                'stream', {
                    'name': 'stdout',
                    'data': self.parser.getMessages()
            })
            ## Setup initial empty content
            content = {}
            if resultObj:
                # We prepare the response with our rich
                # data (the plot).
                content = {
                    'source': 'kernel',

                    # This dictionary may contain
                    # different MIME representations of
                    # the output.
                    'data': {
                        self.mime: resultObj
                    },

                    # We can specify the image size
                    # in the metadata field.
                    'metadata' : {
                        self.mime : {
                            'width': 600,
                            'height': 400
                        }
                    }
                }

            # We send the display_data message with
            # the contents.
            self.send_response(self.iopub_socket,
                'display_data', content)

        # We return the exection results.
        return {'status': 'ok',
                'execution_count':
                    self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    ##
    # Determine completion result
    ##
    def do_complete(self, code, cursor_pos):
        content = {
            # The list of all matches to the completion request, such as
            # ['a.isalnum', 'a.isalpha'] for the above example.
            'matches' : self.complete + self.parser.getModuleNames(),

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
    


####
## Start Jupyter Kernel
##
if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=IOpenSCAD)
