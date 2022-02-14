import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import {
  Collaboration,
  EMPTY_COLLABORATION,
} from '../interfaces/collaboration';

import { UserPermissionService } from 'src/app/auth/services/user-permission.service';
import { OrganizationInCollaboration } from 'src/app/organization/interfaces/organization';
import { Router } from '@angular/router';
import { NodeEditService } from 'src/app/node/services/node-edit.service';

@Component({
  selector: 'app-collaboration-view',
  templateUrl: './collaboration-view.component.html',
  styleUrls: [
    '../../shared/scss/buttons.scss',
    './collaboration-view.component.scss',
  ],
})
export class CollaborationViewComponent implements OnInit {
  @Input() collaboration: Collaboration = EMPTY_COLLABORATION;
  @Output() deletingCollab = new EventEmitter<Collaboration>();
  @Output() editingCollab = new EventEmitter<Collaboration>();
  missing_node_msgs: string[] = [];

  constructor(
    private router: Router,
    public userPermission: UserPermissionService,
    private nodeEditService: NodeEditService
  ) {}

  ngOnInit(): void {
    this.setMissingNodeMsg();
  }

  encrypted(): string {
    return this.collaboration.encrypted ? 'Yes' : 'No';
  }

  getButtonClasses(org: OrganizationInCollaboration): string {
    let default_classes = 'mat-button btn-detail inline ';
    if (!org.node) return default_classes;
    else if (org.node.is_online) return default_classes + 'btn-online';
    else return default_classes + 'btn-offline';
  }

  setMissingNodeMsg(): void {
    this.missing_node_msgs = [];
    for (let org of this.collaboration.organizations) {
      if (!org.node) {
        this.missing_node_msgs.push(
          "No node has been created for organization '" +
            org.name +
            "' in this collaboration!"
        );
      }
    }
  }

  isDisabled(org: OrganizationInCollaboration): boolean {
    return org.node === undefined;
  }

  goToNode(org: OrganizationInCollaboration): void {
    if (org.node) {
      this.nodeEditService.setNode(org.node);
      this.router.navigate([`/node/${org.node.id}/view/${org.id}`]);
    }
  }
}
