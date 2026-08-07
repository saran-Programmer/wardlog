package com.wardlog.timesheetservice.entity;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Embeddable;
import jakarta.persistence.JoinColumn;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

/**
 * Patient details attached to an activity once the AI Service extracts them from
 * conversation. Display-only — no queries filter by these fields, so kept as a
 * simple embedded value rather than its own entity/table.
 */
@Embeddable
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Patient {

    @Column(name = "patient_name")
    private String name;

    @Column(name = "patient_age")
    private Integer age;

    @Column(name = "patient_sex")
    private String sex;

    @ElementCollection
    @CollectionTable(name = "activity_patient_diagnosis", joinColumns = @JoinColumn(name = "activity_id"))
    @Column(name = "diagnosis")
    @Builder.Default
    private List<String> diagnosis = new ArrayList<>();

    @ElementCollection
    @CollectionTable(name = "activity_patient_drug", joinColumns = @JoinColumn(name = "activity_id"))
    @Column(name = "drug")
    @Builder.Default
    private List<String> drugs = new ArrayList<>();
}
