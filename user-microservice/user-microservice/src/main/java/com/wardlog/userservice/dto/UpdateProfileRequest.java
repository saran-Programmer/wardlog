package com.wardlog.userservice.dto;

import com.wardlog.userservice.enums.ToneType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateProfileRequest {

    private String name;

    private Integer age;

    private String sex;

    private String speciality;

    private ToneType tone;

    private String assistantName;
}
