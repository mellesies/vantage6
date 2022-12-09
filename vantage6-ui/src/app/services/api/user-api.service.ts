import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { User } from 'src/app/interfaces/user';

import { getIdsFromArray } from 'src/app/shared/utils';
import { BaseApiService } from 'src/app/services/api/base-api.service';
import { ResType } from 'src/app/shared/enum';
import { ModalService } from 'src/app/services/common/modal.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class UserApiService extends BaseApiService {
  constructor(
    protected http: HttpClient,
    protected modalService: ModalService
  ) {
    super(ResType.USER, http, modalService);
  }

  get_data(
    user: User,
    exclude_own_permissions: boolean = false,
    include_password = true
  ): any {
    let data: any = {
      username: user.username,
      email: user.email,
      firstname: user.first_name,
      lastname: user.last_name,
      organization_id: user.organization_id,
    };
    // do not include the roles/rules of a user that is logged in: they are
    // not allowed to change their own permissions, and this will lead to error
    if (!(user.is_logged_in && exclude_own_permissions)) {
      data.roles = getIdsFromArray(user.roles);
      data.rules = getIdsFromArray(user.rules);
    }
    if (user.password && include_password) {
      data.password = user.password;
    }
    return data;
  }

  update(user: User) {
    const data = this.get_data(user, true, false);
    return this.http.patch<any>(environment.api_url + '/user/' + user.id, data);
  }

  change_password(current_password: string, new_password: string) {
    return this.http.patch<any>(environment.api_url + '/password/change', {
      current_password: current_password,
      new_password: new_password,
    });
  }
}
