# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import license

if __name__ == "__main__":
    if license.License().check_license_status():
        import server
        server.ContractAPI().run()
