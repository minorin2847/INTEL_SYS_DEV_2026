import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme/app_theme.dart';
import '../models/property_input.dart';
import '../providers/prediction_provider.dart';
import '../widgets/preset_bar.dart';
import '../widgets/result_card.dart';
import '../widgets/server_status_badge.dart';
import '../widgets/primitives.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _formKey = GlobalKey<FormState>();

  int _step = 0;
  bool _touched = false;
  PropertyInput? _lastInput;

  final List<String> _sections = [
    'Dimensions',
    'Architecture',
    'Location',
    'Attributes'
  ];

  // Text editing controllers
  late TextEditingController _areaCtrl;
  late TextEditingController _widthCtrl;
  late TextEditingController _lengthCtrl;
  late TextEditingController _alleyWidthCtrl;
  late TextEditingController _bedroomsCtrl;
  late TextEditingController _bathroomsCtrl;
  late TextEditingController _floorsCtrl;
  late TextEditingController _districtCtrl;
  late TextEditingController _wardCtrl;

  // Dropdown states
  String? _propertyType = 'Nhà riêng';
  String? _position = 'Đường chính';
  String? _direction = 'Nam';
  String? _roadType = 'Đường nhựa';
  String? _province = 'an-giang';
  String? _agentRole = 'Chính chủ';

  final List<String> _propertyTypes = [
    'Nhà riêng', 'Căn hộ chung cư', 'Đất', 'Nhà mặt phố', 'Biệt thự', 'Khác'
  ];
  final List<String> _positions = ['Đường chính', 'Trong hẻm', 'Mặt tiền'];
  final List<String> _directions = ['Đông', 'Tây', 'Nam', 'Bắc', 'Đông Nam', 'Đông Bắc', 'Tây Nam', 'Tây Bắc'];
  final List<String> _roadTypes = ['Đường nhựa', 'Đường bê tông', 'Đường đất'];
  final List<Map<String, String>> _provinces = [
    {'slug': 'an-giang', 'name': 'An Giang'},
    {'slug': 'tp-ho-chi-minh', 'name': 'Ho Chi Minh City'},
    {'slug': 'ha-noi', 'name': 'Hanoi'},
    {'slug': 'da-nang', 'name': 'Da Nang'},
    {'slug': 'binh-duong', 'name': 'Binh Duong'},
    {'slug': 'dong-nai', 'name': 'Dong Nai'},
    {'slug': 'can-tho', 'name': 'Can Tho'},
    {'slug': 'hai-phong', 'name': 'Hai Phong'},
    {'slug': 'khanh-hoa', 'name': 'Khanh Hoa'},
    {'slug': 'lam-dong', 'name': 'Lam Dong'},
  ];
  final List<String> _agentRoles = ['Chính chủ', 'Môi giới'];

  @override
  void initState() {
    super.initState();
    _areaCtrl = TextEditingController(text: '78.7');
    _widthCtrl = TextEditingController(text: '4.0');
    _lengthCtrl = TextEditingController(text: '19.6');
    _alleyWidthCtrl = TextEditingController(text: '3.5');
    _bedroomsCtrl = TextEditingController(text: '3');
    _bathroomsCtrl = TextEditingController(text: '2');
    _floorsCtrl = TextEditingController(text: '2');
    _districtCtrl = TextEditingController(text: 'Rạch Giá');
    _wardCtrl = TextEditingController(text: 'Phường An Hòa');
  }

  @override
  void dispose() {
    _areaCtrl.dispose(); _widthCtrl.dispose(); _lengthCtrl.dispose(); _alleyWidthCtrl.dispose();
    _bedroomsCtrl.dispose(); _bathroomsCtrl.dispose(); _floorsCtrl.dispose();
    _districtCtrl.dispose(); _wardCtrl.dispose();
    super.dispose();
  }

  void _applyPresetData(PropertyInput data) {
    setState(() {
      _areaCtrl.text = data.area.toString();
      _widthCtrl.text = data.width?.toString() ?? '';
      _lengthCtrl.text = data.length?.toString() ?? '';
      _alleyWidthCtrl.text = data.alleyWidth?.toString() ?? '';
      _bedroomsCtrl.text = data.bedrooms?.toString() ?? '';
      _bathroomsCtrl.text = data.bathrooms?.toString() ?? '';
      _floorsCtrl.text = data.floors?.toString() ?? '';
      _districtCtrl.text = data.district ?? '';
      _wardCtrl.text = data.ward ?? '';
      _propertyType = data.propertyType ?? _propertyType;
      _position = data.position ?? _position;
      _direction = data.direction ?? _direction;
      _roadType = data.roadType ?? _roadType;
      _province = data.province ?? _province;
      _agentRole = data.agentRole ?? _agentRole;
    });
  }

  bool _validateCurrentStep() {
    if (_step == 0) {
      if (_areaCtrl.text.isEmpty) return false;
      final area = double.tryParse(_areaCtrl.text);
      if (area == null || area <= 0) return false;
    }
    return true;
  }

  void _next() {
    if (!_validateCurrentStep()) {
      setState(() => _touched = true);
      return;
    }
    setState(() => _touched = false);
    if (_step < _sections.length - 1) {
      setState(() => _step += 1);
    } else {
      _handleSubmit();
    }
  }

  void _back() {
    setState(() {
      _touched = false;
      if (_step > 0) _step -= 1;
    });
  }

  void _handleSubmit() {
    if (!_formKey.currentState!.validate()) return;
    
    final input = PropertyInput(
      area: double.parse(_areaCtrl.text),
      width: double.tryParse(_widthCtrl.text),
      length: double.tryParse(_lengthCtrl.text),
      alleyWidth: double.tryParse(_alleyWidthCtrl.text),
      bedrooms: double.tryParse(_bedroomsCtrl.text),
      bathrooms: double.tryParse(_bathroomsCtrl.text),
      floors: double.tryParse(_floorsCtrl.text),
      district: _districtCtrl.text.isEmpty ? null : _districtCtrl.text,
      ward: _wardCtrl.text.isEmpty ? null : _wardCtrl.text,
      propertyType: _propertyType,
      position: _position,
      direction: _direction,
      roadType: _roadType,
      province: _province,
      agentRole: _agentRole,
    );

    setState(() { _lastInput = input; });
    context.read<PredictionProvider>().predict(input);
  }

  String _stepSub(int i) {
    switch (i) {
      case 0: return 'Specify usable floor area and lot boundaries';
      case 1: return 'Select room configuration and structural floors';
      case 2: return 'Select administrative district and plot position';
      default: return 'Choose property classification, road surface, and orientation';
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final provider = context.watch<PredictionProvider>();

    if (provider.result != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Valuation Result')),
        body: ResultCard(
          result: provider.result!,
          input: _lastInput,
          onClear: () {
            provider.clearResult();
            setState(() => _step = 0);
          },
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Real Estate AI Valuation'),
            Text('Vietnam Real Estate Market · predicts Price',
                style: TextStyle(fontSize: Ty.xs, color: c.textSoft)),
          ],
        ),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 12.0),
            child: Center(child: ServerStatusBadge()),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(Sp.s4, Sp.s4, Sp.s4, Sp.s6),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    PresetBar(onSelectPreset: _applyPresetData),
                    const SizedBox(height: Sp.s5),
                    StepperBar(
                      steps: _sections,
                      current: _step,
                      onJump: (i) => setState(() { _step = i; _touched = false; }),
                    ),
                    const SizedBox(height: Sp.s5),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Pill('STEP ${_step + 1} OF ${_sections.length}', tone: 'accent'),
                    ),
                    const SizedBox(height: Sp.s2),
                    Text(_sections[_step], style: TextStyle(fontSize: Ty.xl, fontWeight: FontWeight.w800, color: c.text)),
                    const SizedBox(height: Sp.s1),
                    Text(_stepSub(_step), style: TextStyle(fontSize: Ty.sm, color: c.textSoft)),
                    const SizedBox(height: Sp.s4),
                    
                    if (provider.errorMessage != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        margin: const EdgeInsets.only(bottom: 16),
                        decoration: BoxDecoration(
                          color: c.badWeak,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: c.bad),
                        ),
                        child: Text(
                          'Error: ${provider.errorMessage!}',
                          style: TextStyle(color: c.bad, fontSize: 13),
                        ),
                      ),
                    
                    if (_step == 0) ...[
                      AppCard(
                        child: Column(
                          children: [
                            TextFormField(
                              controller: _areaCtrl,
                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                              decoration: InputDecoration(
                                labelText: 'Usable Area (m²) *',
                                hintText: 'e.g. 78.7',
                                errorText: (_touched && (_areaCtrl.text.isEmpty || double.tryParse(_areaCtrl.text) == null)) ? 'Required field' : null,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: TextFormField(
                                    controller: _widthCtrl,
                                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                    decoration: const InputDecoration(labelText: 'Frontage Width (m)'),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: TextFormField(
                                    controller: _lengthCtrl,
                                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                    decoration: const InputDecoration(labelText: 'Lot Depth (m)'),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            TextFormField(
                              controller: _alleyWidthCtrl,
                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                              decoration: const InputDecoration(labelText: 'Alley Width (m)'),
                            ),
                          ],
                        ),
                      ),
                    ],
                    
                    if (_step == 1) ...[
                      AppCard(
                        child: Row(
                          children: [
                            Expanded(child: TextFormField(controller: _bedroomsCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Bedrooms'))),
                            const SizedBox(width: 8),
                            Expanded(child: TextFormField(controller: _bathroomsCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Bathrooms'))),
                            const SizedBox(width: 8),
                            Expanded(child: TextFormField(controller: _floorsCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Floors'))),
                          ],
                        ),
                      ),
                    ],
                    
                    if (_step == 2) ...[
                      AppCard(
                        child: Column(
                          children: [
                            DropdownButtonFormField<String>(
                              initialValue: _province,
                              decoration: const InputDecoration(labelText: 'Province / City'),
                              items: _provinces.map((p) => DropdownMenuItem(value: p['slug'], child: Text(p['name']!))).toList(),
                              onChanged: (val) => setState(() => _province = val),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(child: TextFormField(controller: _districtCtrl, decoration: const InputDecoration(labelText: 'District / County'))),
                                const SizedBox(width: 12),
                                Expanded(child: TextFormField(controller: _wardCtrl, decoration: const InputDecoration(labelText: 'Ward / Commune'))),
                              ],
                            ),
                            const SizedBox(height: 12),
                            DropdownButtonFormField<String>(
                              initialValue: _position,
                              decoration: const InputDecoration(labelText: 'Property Position'),
                              items: _positions.map((pos) => DropdownMenuItem(value: pos, child: Text(pos))).toList(),
                              onChanged: (val) => setState(() => _position = val),
                            ),
                          ],
                        ),
                      ),
                    ],
                    
                    if (_step == 3) ...[
                      AppCard(
                        child: Column(
                          children: [
                            DropdownButtonFormField<String>(
                              initialValue: _propertyType,
                              decoration: const InputDecoration(labelText: 'Property Type'),
                              items: _propertyTypes.map((pt) => DropdownMenuItem(value: pt, child: Text(pt))).toList(),
                              onChanged: (val) => setState(() => _propertyType = val),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: DropdownButtonFormField<String>(
                              initialValue: _direction,
                                    decoration: const InputDecoration(labelText: 'Direction'),
                                    items: _directions.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
                                    onChanged: (val) => setState(() => _direction = val),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: DropdownButtonFormField<String>(
                              initialValue: _roadType,
                                    decoration: const InputDecoration(labelText: 'Road Access'),
                                    items: _roadTypes.map((r) => DropdownMenuItem(value: r, child: Text(r))).toList(),
                                    onChanged: (val) => setState(() => _roadType = val),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            DropdownButtonFormField<String>(
                              initialValue: _agentRole,
                              decoration: const InputDecoration(labelText: 'Seller Role'),
                              items: _agentRoles.map((role) => DropdownMenuItem(value: role, child: Text(role))).toList(),
                              onChanged: (val) => setState(() => _agentRole = val),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
          Container(
            padding: EdgeInsets.fromLTRB(Sp.s4, Sp.s3, Sp.s4, Sp.s3 + MediaQuery.of(context).padding.bottom),
            decoration: BoxDecoration(color: c.surface, border: Border(top: BorderSide(color: c.border))),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                AppButton(label: '← Back', onPressed: _step == 0 || provider.isSubmitting ? null : _back),
                AppButton(
                  label: _step == _sections.length - 1 ? (provider.isSubmitting ? 'Scoring…' : 'Predict') : 'Next',
                  primary: true,
                  busy: provider.isSubmitting,
                  onPressed: provider.isSubmitting ? null : _next,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}


class StepperBar extends StatelessWidget {
  final List<String> steps;
  final int current;
  final ValueChanged<int> onJump;

  const StepperBar({
    super.key,
    required this.steps,
    required this.current,
    required this.onJump,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(steps.length * 2 - 1, (index) {
        if (index % 2 == 1) {
          return Expanded(
            child: Container(
              height: 2,
              color: index ~/ 2 < current ? context.c.accent : context.c.border,
            ),
          );
        }
        final stepIndex = index ~/ 2;
        final isActive = stepIndex == current;
        final isPast = stepIndex < current;
        return GestureDetector(
          onTap: () => isPast ? onJump(stepIndex) : null,
          child: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isActive ? context.c.accent : (isPast ? context.c.accent : context.c.surface2),
              border: isActive || isPast ? null : Border.all(color: context.c.border),
            ),
            child: Center(
              child: isPast
                  ? Icon(Icons.check, size: 16, color: context.c.accentInk)
                  : Text(
                      '${stepIndex + 1}',
                      style: TextStyle(
                        color: isActive ? context.c.accentInk : context.c.textFaint,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
            ),
          ),
        );
      }),
    );
  }
}
