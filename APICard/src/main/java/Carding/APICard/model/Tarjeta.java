package Carding.APICard.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "tarjetas")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Tarjeta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_tarjeta")
    private Long idTarjeta;

    @NotBlank(message = "El número de tarjeta es obligatorio")
    @Pattern(regexp = "\\d{16}", message = "El número debe tener 16 dígitos")
    @Column(name = "numero", nullable = false)
    private String numero;

    @NotNull(message = "El mes es obligatorio")
    @Min(value = 1, message = "El mes debe ser entre 1 y 12")
    @Max(value = 12, message = "El mes debe ser entre 1 y 12")
    @Column(name = "mes", nullable = false)
    private Integer mes;

    @NotNull(message = "El año es obligatorio")
    @Min(value = 2024, message = "El año debe ser mayor o igual a 2024")
    @Max(value = 2100, message = "El año debe ser menor o igual a 2100")
    @Column(name = "anio", nullable = false)
    private Integer anio;

    @NotNull(message = "El CCV es obligatorio")
    @Min(value = 100, message = "El CCV debe tener 3 dígitos")
    @Max(value = 999, message = "El CCV debe tener 3 dígitos")
    @Column(name = "ccv", nullable = false)
    private Integer ccv;
}