import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { EMPTY_NODE, Node } from 'src/app/node/interfaces/node';

import { ConvertJsonService } from 'src/app/shared/services/convert-json.service';
import { ModalService } from 'src/app/modal/modal.service';
import { Resource } from 'src/app/shared/enum';
import { ApiService } from 'src/app/shared/services/api.service';
import { environment } from 'src/environments/environment';
import { ModalMessageComponent } from 'src/app/modal/modal-message/modal-message.component';

@Injectable({
  providedIn: 'root',
})
export class ApiNodeService extends ApiService {
  constructor(
    protected http: HttpClient,
    private convertJsonService: ConvertJsonService,
    protected modalService: ModalService
  ) {
    super(Resource.NODE, http, modalService);
  }

  async reset_api_key(node: Node): Promise<string | null> {
    let data = { id: node.id };
    try {
      let response = await this.http
        .post<any>(environment.api_url + '/recover/node', data)
        .toPromise();
      return response.api_key;
    } catch (error: any) {
      this.modalService.openMessageModal(ModalMessageComponent, [
        'Error: ' + error.error.msg,
      ]);
      return null;
    }
  }

  get_data(node: Node): any {
    let data: any = {
      name: node.name,
    };
    return data;
  }

  async getNode(id: number): Promise<Node> {
    let node = await super.getResource(id, this.convertJsonService.getNode);
    return node === null ? EMPTY_NODE : node;
  }

  async getNodes(force_refresh: boolean = false) {
    return await super.getResources(
      force_refresh,
      this.convertJsonService.getNode
    );
  }
}
