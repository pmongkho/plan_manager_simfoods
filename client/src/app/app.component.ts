import { Component, OnInit } from '@angular/core'
import { ApiService } from './services/api.service'
import { FormsModule } from '@angular/forms' // Import FormsModule
import { CommonModule } from '@angular/common' // Import CommonModule for directives like ngIf
import {RouterModule} from '@angular/router'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule], // Import FormsModule and CommonModule
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent  {
}