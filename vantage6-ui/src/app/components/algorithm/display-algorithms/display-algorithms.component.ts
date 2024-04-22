import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { Algorithm } from 'src/app/models/api/algorithm.model';
import { routePaths } from 'src/app/routes';

@Component({
  selector: 'app-display-algorithms',
  templateUrl: './display-algorithms.component.html',
  styleUrl: './display-algorithms.component.scss'
})
export class DisplayAlgorithmsComponent {
  @Input() algorithms: Algorithm[] = [];
  routePaths = routePaths;

  constructor(private router: Router) {}

  handleAlgorithmClick(algorithm: Algorithm) {
    this.router.navigate([routePaths.algorithm, algorithm.id, algorithm.algorith_store_id]);
  }
}
