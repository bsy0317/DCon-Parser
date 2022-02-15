import unicodedata   
import requests

class DC_CON:
    def getList(self,package_name):
        main_dict = dict()
        data = requests.get(f"https://dccon.dcinside.com/hot/1/title/{package_name}",headers=self.default_headers())
        data_sec_1 = data.text.split('<li class="div_package "')
        for i in range(1,len(data_sec_1)):
            data_sec_2 = data_sec_1[i].split('</li>')[0]
            package_idx = data_sec_2.split('package_idx="')[1].split('">')[0]
            dcon_name = data_sec_2.split('<strong class="dcon_name">')[1].split('</strong>')[0]
            dcon_seller = data_sec_2.split('<span class="dcon_seller">')[1].split('</span>')[0]
            main_dict[package_idx] = [package_idx,dcon_name,dcon_seller]
        return main_dict
        
    def default_headers(self):
        return dict({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept-Encoding': ', '.join(('gzip', 'deflate')),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Host':'dccon.dcinside.com',
        })