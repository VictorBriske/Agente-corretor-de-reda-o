import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface ValidationError {
  field: string;
  message: string;
}

@Component({
  selector: 'app-redacao-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './redacao-form.component.html',
  styleUrl: './redacao-form.component.scss'
})
export class RedacaoFormComponent {
  @Output() enviarRedacao = new EventEmitter<{titulo: string, redacao: string, tema: string}>();

  titulo = '';
  redacao = '';
  tema = 'livre';
  isLoading = false;
  validationErrors: ValidationError[] = [];
  showValidationErrors = false;

  // Constantes de validação
  readonly MIN_TITULO_LENGTH = 5;
  readonly MIN_REDACAO_LENGTH = 100;
  readonly RECOMMENDED_REDACAO_LENGTH = 500; // Recomendado para uma redação completa
  readonly MAX_REDACAO_LENGTH = 10000;

  temasFixos = [
    'livre',
    'Desafios para a valorização de comunidades e povos tradicionais no Brasil',
    'Caminhos para combater a intolerância religiosa no Brasil',
    'Desafios para a formação educacional de surdos no Brasil',
    'Invisibilidade e registro civil: garantia de acesso à cidadania no Brasil',
    'Democratização do acesso ao cinema no Brasil'
  ];

  get isValid(): boolean {
    return this.titulo.trim().length >= this.MIN_TITULO_LENGTH && 
           this.redacao.trim().length >= this.MIN_REDACAO_LENGTH &&
           this.redacao.trim().length <= this.MAX_REDACAO_LENGTH;
  }

  get redacaoLength(): number {
    return this.redacao.trim().length;
  }

  get isRedacaoTooShort(): boolean {
    return this.redacaoLength > 0 && this.redacaoLength < this.MIN_REDACAO_LENGTH;
  }

  get isRedacaoRecommended(): boolean {
    return this.redacaoLength >= this.RECOMMENDED_REDACAO_LENGTH;
  }

  get isRedacaoTooLong(): boolean {
    return this.redacaoLength > this.MAX_REDACAO_LENGTH;
  }

  validateForm(): ValidationError[] {
    const errors: ValidationError[] = [];

    // Validar título
    if (!this.titulo.trim()) {
      errors.push({
        field: 'titulo',
        message: 'O título é obrigatório'
      });
    } else if (this.titulo.trim().length < this.MIN_TITULO_LENGTH) {
      errors.push({
        field: 'titulo',
        message: `O título deve ter no mínimo ${this.MIN_TITULO_LENGTH} caracteres`
      });
    }

    // Validar redação
    if (!this.redacao.trim()) {
      errors.push({
        field: 'redacao',
        message: 'A redação é obrigatória'
      });
    } else if (this.redacaoLength < this.MIN_REDACAO_LENGTH) {
      errors.push({
        field: 'redacao',
        message: `A redação deve ter no mínimo ${this.MIN_REDACAO_LENGTH} caracteres. Você digitou ${this.redacaoLength} caracteres.`
      });
    } else if (this.redacaoLength > this.MAX_REDACAO_LENGTH) {
      errors.push({
        field: 'redacao',
        message: `A redação não pode ter mais de ${this.MAX_REDACAO_LENGTH} caracteres. Você digitou ${this.redacaoLength} caracteres.`
      });
    } else if (this.redacaoLength < this.RECOMMENDED_REDACAO_LENGTH) {
      errors.push({
        field: 'redacao',
        message: `Recomendamos que a redação tenha pelo menos ${this.RECOMMENDED_REDACAO_LENGTH} caracteres para uma análise mais completa. Você digitou ${this.redacaoLength} caracteres.`
      });
    }

    return errors;
  }

  onSubmit() {
    this.validationErrors = this.validateForm();
    this.showValidationErrors = true;

    if (this.validationErrors.length === 0 && !this.isLoading) {
      this.enviarRedacao.emit({ 
        titulo: this.titulo.trim(),
        redacao: this.redacao.trim(), 
        tema: this.tema 
      });
      this.showValidationErrors = false;
    }
  }

  setLoading(loading: boolean) {
    this.isLoading = loading;
  }

  getFieldErrors(field: string): string[] {
    return this.validationErrors
      .filter(error => error.field === field)
      .map(error => error.message);
  }

  hasFieldError(field: string): boolean {
    return this.showValidationErrors && this.getFieldErrors(field).length > 0;
  }
}
