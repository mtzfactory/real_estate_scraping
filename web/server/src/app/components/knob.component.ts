import { ViewChild, ElementRef, AfterViewInit, Component, Input } from '@angular/core';

declare var jQuery: any;

@Component({
  selector: 'app-knob',
  template: `<input #input type="text" class="dial" readonly>`
})
export class KnobComponent implements AfterViewInit {
  @Input() val: number;
  @Input() min: number;
  @Input() max: number;
  @Input() size: number;
  @Input() thickness: number;
  @Input() fgcolor: number;
  @Input() bgcolor: number;
  @ViewChild('input') input: ElementRef;

  ngAfterViewInit() {
    jQuery(this.input.nativeElement).knob({
      'min': this.min || 0,
      'max': this.max || 2 * this.val,
      'width': this.size || 75,
      'height': this.size || 75,
      'thickness': this.thickness || 0.3,
      'fgColor': this.fgcolor || '#87CEEB',
      'bgColor': this.bgcolor || '#EEEEEE'
    });
    jQuery(this.input.nativeElement).val(this.val).trigger('change');
  }
}

// http://anthonyterrien.com/knob/
// http://www.radzen.com/blog/jquery-plugins-and-angular/
