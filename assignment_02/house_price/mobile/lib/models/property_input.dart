class PropertyInput {
  double area;
  double? width;
  double? length;
  double? bedrooms;
  double? bathrooms;
  double? floors;
  double? alleyWidth;
  double? agentListingCount;
  String? propertyType;
  String? position;
  String? direction;
  String? roadType;
  String? province;
  String? agentRole;
  String? ward;
  String? district;

  PropertyInput({
    required this.area,
    this.width,
    this.length,
    this.bedrooms,
    this.bathrooms,
    this.floors,
    this.alleyWidth,
    this.agentListingCount,
    this.propertyType,
    this.position,
    this.direction,
    this.roadType,
    this.province,
    this.agentRole,
    this.ward,
    this.district,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'Area': area,
    };

    if (width != null) map['Width'] = width;
    if (length != null) map['Length'] = length;
    if (bedrooms != null) map['Bedrooms'] = bedrooms;
    if (bathrooms != null) map['Bathrooms'] = bathrooms;
    if (floors != null) map['Floors'] = floors;
    if (alleyWidth != null) map['Alley Width'] = alleyWidth;
    if (agentListingCount != null) map['Agent Listing Count'] = agentListingCount;
    if (propertyType != null && propertyType!.isNotEmpty) {
      map['Property Type'] = propertyType;
    }
    if (position != null && position!.isNotEmpty) map['Position'] = position;
    if (direction != null && direction!.isNotEmpty) map['Direction'] = direction;
    if (roadType != null && roadType!.isNotEmpty) map['Road Type'] = roadType;
    if (province != null && province!.isNotEmpty) map['Province'] = province;
    if (agentRole != null && agentRole!.isNotEmpty) map['Agent Role'] = agentRole;
    if (ward != null && ward!.isNotEmpty) map['ward'] = ward;
    if (district != null && district!.isNotEmpty) map['district'] = district;

    return map;
  }

  PropertyInput copyWith({
    double? area,
    double? width,
    double? length,
    double? bedrooms,
    double? bathrooms,
    double? floors,
    double? alleyWidth,
    double? agentListingCount,
    String? propertyType,
    String? position,
    String? direction,
    String? roadType,
    String? province,
    String? agentRole,
    String? ward,
    String? district,
  }) {
    return PropertyInput(
      area: area ?? this.area,
      width: width ?? this.width,
      length: length ?? this.length,
      bedrooms: bedrooms ?? this.bedrooms,
      bathrooms: bathrooms ?? this.bathrooms,
      floors: floors ?? this.floors,
      alleyWidth: alleyWidth ?? this.alleyWidth,
      agentListingCount: agentListingCount ?? this.agentListingCount,
      propertyType: propertyType ?? this.propertyType,
      position: position ?? this.position,
      direction: direction ?? this.direction,
      roadType: roadType ?? this.roadType,
      province: province ?? this.province,
      agentRole: agentRole ?? this.agentRole,
      ward: ward ?? this.ward,
      district: district ?? this.district,
    );
  }
}
