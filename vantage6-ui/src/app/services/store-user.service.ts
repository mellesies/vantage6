import { Injectable } from '@angular/core';
import { StoreUser, StoreUserFormSubmit, StoreUserLazyProperties, getStoreUserParameters } from '../models/api/store-user.model';
import { Pagination } from '../models/api/pagination.model';
import { ApiService } from './api.service';
import { getLazyProperties } from '../helpers/api.helper';

@Injectable({
  providedIn: 'root'
})
export class StoreUserService {
  constructor(private apiService: ApiService) {}

  async getPaginatedUsers(store_url: string, currentPage: number, parameters?: getStoreUserParameters): Promise<Pagination<StoreUser>> {
    const result = await this.apiService.getForAlgorithmApiWithPagination<StoreUser>(store_url, `/api/user`, currentPage, {
      ...parameters
    });
    return result;
  }

  async getUser(store_url: string, id: string, lazyProperties: StoreUserLazyProperties[] = []): Promise<StoreUser> {
    const result = await this.apiService.getForAlgorithmApi<StoreUser>(store_url, `/api/user/${id}`);

    const user = { ...result, roles: [] };
    await getLazyProperties(result, user, lazyProperties, this.apiService, store_url);

    return user;
  }

  async editUser(store_url: string, id: number, user: StoreUserFormSubmit): Promise<StoreUser> {
    const result = await this.apiService.patchForAlgorithmApi<StoreUser>(store_url, `/api/user/${id}`, user);
    return result;
  }
}
