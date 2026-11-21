"""Offline protocol fixtures: no model, agent, account, file-vault or browser calls."""
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import msshi_interaction as provision
SPEC=importlib.util.spec_from_file_location('interaction_fixture',ROOT/'hermes_plugins/msshi-interaction/__init__.py')
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

def config():
    return {'model':{'provider':'chosen-provider','default':'chosen-main'},
        'moa':{'enabled':True,'default_preset':'chosen','presets':{'chosen':{'enabled':True,
        'reference_models':[{'provider':'chosen-provider','model':'review-'+str(i)} for i in range(3)],
        'aggregator':{'provider':'chosen-provider','model':'integrator'}}}}}

class Llm:
    def __init__(self,fail=False,requests=None):self.calls=[];self.fail=fail;self.requests=requests or []
    def complete(self,**kwargs):
        self.calls.append(kwargs)
        if self.fail:raise TimeoutError('fixture timeout')
        value=json.dumps({'blueprint':'Centralized plan from supplied evidence','source_requests':self.requests,'limitations':[]}) if kwargs['task'].endswith('aggregator') else 'Critical review with a concrete improvement.'
        return SimpleNamespace(text=value)

class Lifecycle:
    def __init__(self):self.requests=[];self.cancelled=False
    def launch(self,request):
        self.requests.append(request)
        if request.get('timeout_seconds') is not None:raise ValueError('Native API does not support per-launch timeout')
        if 'provider' in request or 'model' in request:raise AssertionError('Do not override user delegation choices')
        return SimpleNamespace(to_dict=lambda:{'subagent_id':'fixture-child','capability':'fixture-capability'})
    def result(self,handle):return SimpleNamespace(ready=True,terminal_state='SUCCEEDED',summary='Advisor checked the plan.',usage_metadata={'api_calls':1})
    def cancel(self,handle,reason):self.cancelled=True

class InteractionControllerTests(unittest.TestCase):
    def controller(self,home,role='shikaku',cfg=None,llm=None,life=None,session='fixture-session',reader=None):
        return mod.Controller(Path(home),role,lambda:session,llm=llm,lifecycle=life,config=config() if cfg is None else cfg,
            register_task=lambda *args,**kwargs:None,config_reader=reader)
    def begin(self,c,confirmed=True,**kwargs):
        return c.begin({'scope':'Implement one bounded feature','initial_plan':'Understand, implement, test, review.',
                        'confirmed':confirmed,**kwargs})['job_id']

    def test_registration_status_begin_never_call_model(self):
        with TemporaryDirectory() as tmp:
            llm=Llm(fail=True);c=self.controller(tmp,llm=llm)
            c.summary();self.begin(c);self.assertEqual(llm.calls,[])
    def test_two_rounds_require_main_audit_and_final_approval(self):
        with TemporaryDirectory() as tmp:
            llm=Llm();c=self.controller(tmp,llm=llm);job=self.begin(c)
            first=c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(first['state'],'ROUND1_COMPLETE');self.assertEqual(len(llm.calls),4)
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'council_round'})
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'approve','message':'Too early'})
            c.step({'job_id':job,'action':'audit','message':'Check the design against supplied constraints.'})
            second=c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(second['rounds_completed'],2);self.assertEqual(len(llm.calls),8)
            self.assertEqual([v['task'].rsplit('_',1)[-1] for v in llm.calls],['1','2','3','aggregator']*2)
            approved=c.step({'job_id':job,'action':'approve','message':'Main checked the final blueprint.'})
            self.assertEqual(approved['state'],'READY_EXECUTION');self.assertFalse(approved['user_approval_granted'])
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'council_round'})
    def test_type_two_never_launches_subagent(self):
        with TemporaryDirectory() as tmp:
            life=Lifecycle();c=self.controller(tmp,llm=Llm(),life=life);job=self.begin(c)
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'advisor'})
            c.step({'job_id':job,'action':'council_round'});self.assertEqual(life.requests,[])
    def test_type_one_native_advisor_without_moa_or_model_override(self):
        with TemporaryDirectory() as tmp:
            life=Lifecycle();llm=Llm(fail=True)
            c=self.controller(tmp,role='yukino',cfg={'delegation':{'provider':'chosen','model':'advisor-choice'}},llm=llm,life=life)
            job=self.begin(c);c.step({'job_id':job,'action':'advisor'})
            self.assertEqual(life.requests[0]['allowed_toolsets'],('msshi-advisor-context',))
            self.assertEqual(c.step({'job_id':job,'action':'advisor_result'})['state'],'ADVISOR_COMPLETE')
            self.assertEqual(c.step({'job_id':job,'action':'approve','message':'Plan polished by Main.'})['state'],'READY_EXECUTION')
            self.assertEqual(llm.calls,[])
    def test_type_one_missing_advisor_fails_closed(self):
        with TemporaryDirectory() as tmp:
            life=Lifecycle();c=self.controller(tmp,role='shizuka',cfg={},life=life);job=self.begin(c)
            with self.assertRaisesRegex(ValueError,'NEEDS_ADVISOR_CONFIG'):c.step({'job_id':job,'action':'advisor'})
            self.assertEqual(life.requests,[])
    def test_val_without_explicit_config_no_native_default_models(self):
        with TemporaryDirectory() as tmp:
            llm=Llm(fail=True);c=self.controller(tmp,role='val',cfg={'model':{'provider':'own','default':'own-choice'}},llm=llm)
            self.assertEqual(c.summary()['council_readiness'],'NEEDS_COUNCIL_CONFIG')
            job=self.begin(c)
            with self.assertRaisesRegex(ValueError,'NEEDS_COUNCIL_CONFIG'):c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(llm.calls,[])
    def test_unconfirmed_direct_and_forwarded_are_not_chargeable(self):
        with TemporaryDirectory() as tmp:
            llm=Llm(fail=True);c=self.controller(tmp,llm=llm)
            direct=self.begin(c,False)
            with self.assertRaises(ValueError):c.step({'job_id':direct,'action':'council_round'})
            forwarded=self.begin(c,False,origin='forwarded',sender='shizuka')
            q=c.step({'job_id':forwarded,'action':'clarify','message':'Short answer or full project?'})
            self.assertEqual(q['clarification_target'],'shizuka')
            q=c.step({'job_id':forwarded,'action':'clarify','message':'Sender needs the User decision','sender_needs_user':True})
            self.assertEqual(q['clarification_target'],'Pengguna');self.assertEqual(q['clarification_hops'],1)
            self.assertEqual(llm.calls,[])
    def test_sources_remain_requests_not_claimed_as_fetched(self):
        with TemporaryDirectory() as tmp:
            llm=Llm(requests=[{'query':'Primary documentation on the chosen interface','reason':'Confirm compatibility'}])
            c=self.controller(tmp,llm=llm);job=self.begin(c)
            output=c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(output['source_requests'][0]['status'],'REQUESTED_NOT_FETCHED')
            c.step({'job_id':job,'action':'audit','message':'Main supplied checked evidence.',
                'evidence':[{'source':'https://example.org/official','summary':'Main checked the authorized primary source.'}]})
            c.step({'job_id':job,'action':'council_round'})
            with self.assertRaisesRegex(ValueError,'Unresolved source'):c.step({'job_id':job,'action':'approve','message':'Main review'})
    def test_timeout_does_not_advance_or_retry_paid_work(self):
        with TemporaryDirectory() as tmp:
            llm=Llm(fail=True);c=self.controller(tmp,llm=llm);job=self.begin(c)
            with self.assertRaises(TimeoutError):c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(c._load(job)['state'],'FAILED')
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(len(llm.calls),1)
    def test_config_change_requires_reload_instead_of_stale_route(self):
        with TemporaryDirectory() as tmp:
            changed=config();changed['moa']['presets']['chosen']['aggregator']['model']='new-own-choice'
            llm=Llm();c=self.controller(tmp,llm=llm,reader=lambda:changed);job=self.begin(c)
            with self.assertRaisesRegex(ValueError,'CONFIG_CHANGED_RELOAD_PLUGIN'):c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(llm.calls,[])
    def test_legacy_flat_explicit_bindings_beside_unselected_preset(self):
        raw=config();preset=raw['moa']['presets']['chosen']
        raw['moa'].pop('default_preset');raw['moa'].update(preset)
        refs,agg,state,shared=mod.council_binding(raw)
        self.assertEqual(len(refs),3);self.assertIsNotNone(agg)
        self.assertEqual(state,'CONFIGURED_NOT_PROVIDER_TESTED')
    def test_clarification_after_round_one_resumes_without_paid_restart(self):
        with TemporaryDirectory() as tmp:
            llm=Llm();c=self.controller(tmp,llm=llm);job=self.begin(c)
            c.step({'job_id':job,'action':'council_round'})
            c.step({'job_id':job,'action':'clarify','message':'Confirm one constraint before proceeding.'})
            answer=c.step({'job_id':job,'action':'confirm','confirmed':True,'message':'Continue with the existing boundary.'})
            self.assertEqual(answer['state'],'ROUND1_COMPLETE')
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(len(llm.calls),4)
    def test_source_resolution_after_round_two_requires_known_nonempty_evidence(self):
        with TemporaryDirectory() as tmp:
            query='Primary documentation'
            llm=Llm(requests=[{'query':query,'reason':'Verify support'}]);c=self.controller(tmp,llm=llm);job=self.begin(c)
            c.step({'job_id':job,'action':'council_round'})
            c.step({'job_id':job,'action':'audit','message':'Main audited first plan.'})
            c.step({'job_id':job,'action':'council_round'})
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'resolve_sources','resolutions':[{'query':query,'evidence_sources':[]}]})
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'resolve_sources','resolutions':[{'query':'unknown','evidence_sources':['source-A']}]})
            result=c.step({'job_id':job,'action':'resolve_sources','evidence':[{'source':'source-A','summary':'Main checked the authorized document.'}],
                'resolutions':[{'query':query,'evidence_sources':['source-A']}]})
            self.assertEqual(result['source_requests'][0]['status'],'RESOLVED_BY_MAIN_INPUT')
            self.assertEqual(result['additional_model_calls'],0);self.assertEqual(len(llm.calls),8)
            self.assertEqual(c.step({'job_id':job,'action':'approve','message':'Main verified the final evidence.'})['state'],'READY_EXECUTION')
    def test_jobs_cannot_cross_sessions_or_paths(self):
        with TemporaryDirectory() as tmp:
            a=self.controller(tmp);job=self.begin(a)
            b=self.controller(tmp,session='other')
            with self.assertRaises(ValueError):b._load(job)
            with self.assertRaises(ValueError):a._load('../secret')
    def test_cancelled_job_cannot_run(self):
        with TemporaryDirectory() as tmp:
            llm=Llm(fail=True);c=self.controller(tmp,llm=llm);job=self.begin(c)
            c.step({'job_id':job,'action':'cancel'})
            with self.assertRaises(ValueError):c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(llm.calls,[])
    def test_native_registration_does_not_inject_missing_user_council(self):
        with TemporaryDirectory() as tmp:
            tasks=[]
            context=SimpleNamespace(profile_name='val',llm=Llm(fail=True),subagent_lifecycle=Lifecycle(),
                get_config=lambda key,default:default,register_auxiliary_task=lambda *a,**k:tasks.append(k),
                register_tool=lambda **kw:None,register_hook=lambda *a:None)
            hc=types.ModuleType('hermes_constants');hc.get_hermes_home=lambda:tmp
            cfg=types.ModuleType('hermes_cli.config');cfg.read_raw_config=lambda:{}
            cfg.load_config_readonly=lambda:config()
            with patch.dict(sys.modules,{'hermes_constants':hc,'hermes_cli.config':cfg}):
                mod.register(context)
            self.assertEqual(tasks,[])
            self.assertEqual(context.llm.calls,[])

    def test_registration_native_approval_has_distinct_round_keys(self):
        with TemporaryDirectory() as tmp:
            context=SimpleNamespace(profile_name='shikaku',llm=Llm(),subagent_lifecycle=Lifecycle(),
                get_config=lambda key,default:default,register_auxiliary_task=lambda *a,**k:None)
            tools={};hooks={}
            context.register_tool=lambda **kw:tools.update({kw['name']:kw})
            context.register_hook=lambda name,callback:hooks.update({name:callback})
            hc=types.ModuleType('hermes_constants');hc.get_hermes_home=lambda:tmp
            cfg=types.ModuleType('hermes_cli.config');cfg.read_raw_config=config
            with patch.dict(sys.modules,{'hermes_constants':hc,'hermes_cli.config':cfg}),patch.object(mod,'_host_session',lambda:'fixture-session'):
                mod.register(context)
            raw=tools['msshi_interaction_begin']['handler']({'scope':'Feature','initial_plan':'Plan','confirmed':True})
            job=json.loads(raw)['job_id']
            first=hooks['pre_tool_call']('msshi_interaction_step',{'job_id':job,'action':'council_round'})
            self.assertEqual(first['action'],'approve');self.assertTrue(first['rule_key'].endswith('round-1'))
            controller=self.controller(tmp);data=controller._load(job);data['rounds_completed']=1;controller._save(data)
            second=hooks['pre_tool_call']('msshi_interaction_step',{'job_id':job,'action':'council_round'})
            self.assertTrue(second['rule_key'].endswith('round-2'));self.assertNotEqual(first['rule_key'],second['rule_key'])
            self.assertEqual(context.llm.calls,[])

    def test_interaction_prompt_section_both_layouts_low_ram_and_length_budget(self):
        import msshi_hermes_profiles as hp
        with TemporaryDirectory() as tmp:
            home=Path(tmp)
            # 1. Verify register() wires msshi.interaction-protocol via register_system_prompt_section
            sections={}
            context=SimpleNamespace(profile_name='val',llm=Llm(fail=True),subagent_lifecycle=Lifecycle(),
                get_config=lambda key,default:default,register_auxiliary_task=lambda *a,**k:None,
                register_tool=lambda **kw:None,register_hook=lambda *a:None,
                register_system_prompt_section=lambda sid,fn,**kw:sections.update({sid:(fn,kw)}))
            hc=types.ModuleType('hermes_constants');hc.get_hermes_home=lambda:home/'profiles/val'
            cfg=types.ModuleType('hermes_cli.config');cfg.read_raw_config=config
            with patch.dict(sys.modules,{'hermes_constants':hc,'hermes_cli.config':cfg}):
                mod.register(context)
            self.assertIn('msshi.interaction-protocol',sections)
            fn,kw=sections['msshi.interaction-protocol']
            self.assertEqual(kw['max_chars'],1800)
            rendered=fn({'profile_name':'val'})
            self.assertLess(len(rendered),1800)
            self.assertIn('Tier 0 (fast_main_only)',rendered)
            self.assertIn('Tier 2 (Type 2 Council)',rendered)

            # 2. Verify all 6 profiles across both layouts (keep-hermes & yukino) and normal vs light modes
            for layout in ('keep-hermes','yukino'):
                hp.record_team_layout(home,layout)
                for res_mode in ('normal','light'):
                    for prof in ('default','yukino','shizuka','val','kiki-chii','shikaku'):
                        text=mod.interaction_policy({'profile_name':prof},home=home,resource_profile=res_mode)
                        self.assertLess(len(text),1800,f'prompt too long for {layout}/{res_mode}/{prof}: {len(text)}')
                        self.assertIn('Tier 0 (fast_main_only)',text)
                        self.assertIn('msshi_find_skill',text)
                        if res_mode=='light':
                            self.assertIn('Low-RAM light mode',text)
                        elif prof in ('yukino','shizuka') or (layout=='yukino' and prof=='default'):
                            self.assertIn('Tier 1 (Type 1 Advisor)',text)
                        elif prof in ('val','kiki-chii','shikaku'):
                            self.assertIn('Tier 2 (Type 2 Council)',text)
                            self.assertIn('Mandatory Main audit',text)
                        else:
                            self.assertIn('Neutral default assistant',text)

    def test_stale_lock_recovery_active_process_concurrent_and_interrupted_paid_step(self):
        import threading
        with TemporaryDirectory() as tmp:
            llm=Llm();c=self.controller(tmp,llm=llm);job=self.begin(c)
            lock=c._lock_path(job)

            # A. Active live PID lock cannot be bypassed or recovered
            lock.write_text(json.dumps({'pid':424242,'created_at':1000.0,'action':'council_round'}),encoding='utf-8')
            with patch.object(mod,'_pid_alive',return_value=True):
                self.assertEqual(c.status_report({'job_id':job})['lock_status'],'active')
                with self.assertRaisesRegex(ValueError,'JOB_BUSY_ACTIVE'):
                    c.step({'job_id':job,'action':'audit','message':'Blocked while live'})
                with self.assertRaisesRegex(ValueError,'JOB_BUSY_ACTIVE'):
                    c.step({'job_id':job,'action':'recover_lock'})
                self.assertTrue(lock.exists())

            # B. Dead PID stale lock during non-paid state (ROUND1_COMPLETE) recovers cleanly without repeating round 1
            lock.unlink()
            c.step({'job_id':job,'action':'council_round'})
            self.assertEqual(len(llm.calls),4)
            lock.write_text(json.dumps({'pid':999991,'created_at':1000.0,'action':'audit'}),encoding='utf-8')
            with patch.object(mod,'_pid_alive',return_value=False):
                self.assertEqual(c.status_report({'job_id':job})['lock_status'],'stale')
                with self.assertRaisesRegex(ValueError,'STALE_LOCK_DETECTED'):
                    c.step({'job_id':job,'action':'audit','message':'Needs explicit recovery first'})
                # Cross-session/cross-bot cannot recover someone else's lock
                other=self.controller(tmp,session='other-session',llm=llm)
                with self.assertRaises(ValueError):
                    other.step({'job_id':job,'action':'recover_lock'})
                self.assertTrue(lock.exists())
                rec=c.step({'job_id':job,'action':'recover_lock'})
                self.assertTrue(rec['lock_recovered']);self.assertFalse(rec['paid_retry_blocked'])
                self.assertEqual(rec['state'],'ROUND1_COMPLETE');self.assertEqual(rec['additional_model_calls'],0)
                self.assertFalse(lock.exists())
                audited=c.step({'job_id':job,'action':'audit','message':'Continues cleanly after recovery'})
                self.assertEqual(audited['state'],'MAIN_AUDITED')
                self.assertEqual(len(llm.calls),4)

            # C. Dead PID stale lock left mid-paid-step (COUNCIL_RUNNING) marks INTERRUPTED and blocks paid retry
            job2=self.begin(c)
            d2=c._load(job2);d2['state']='COUNCIL_RUNNING';d2['calls_attempted']=2;c._save(d2)
            lock2=c._lock_path(job2)
            lock2.write_text('888882',encoding='utf-8')  # legacy plain-int PID format
            with patch.object(mod,'_pid_alive',return_value=False):
                rec2=c.step({'job_id':job2,'action':'recover_lock'})
                self.assertTrue(rec2['lock_recovered']);self.assertTrue(rec2['paid_retry_blocked'])
                self.assertEqual(rec2['state'],'INTERRUPTED');self.assertEqual(rec2['interrupted_from'],'COUNCIL_RUNNING')
                self.assertEqual(rec2['calls_attempted'],2);self.assertEqual(rec2['additional_model_calls'],0)
                with self.assertRaisesRegex(ValueError,'terminal'):
                    c.step({'job_id':job2,'action':'council_round'})

            # D. Two concurrent in-process requests on same job -> second rejected with JOB_BUSY_ACTIVE
            job3=self.begin(c)
            entered=threading.Event();release=threading.Event();errors=[]
            class BlockingLlm(Llm):
                def complete(self,**kwargs):
                    entered.set();release.wait(timeout=3)
                    return super().complete(**kwargs)
            c_conc=self.controller(tmp,llm=BlockingLlm())
            t1=threading.Thread(target=lambda:c_conc.step({'job_id':job3,'action':'council_round'}))
            t1.start()
            self.assertTrue(entered.wait(timeout=3))
            try:
                c_conc.step({'job_id':job3,'action':'audit','message':'Concurrent conflict'})
            except ValueError as exc:
                errors.append(str(exc))
            finally:
                release.set();t1.join(timeout=3)
            self.assertTrue(any('JOB_BUSY_ACTIVE' in e for e in errors),f'Expected JOB_BUSY_ACTIVE, got {errors}')

    def test_session_job_summaries_bot_isolation_legacy_compat_and_retention(self):
        with TemporaryDirectory() as tmp:
            val_a=self.controller(tmp,role='val',session='sess-A',llm=Llm())
            val_b=self.controller(tmp,role='val',session='sess-B',llm=Llm())
            shi_a=self.controller(tmp,role='shikaku',session='sess-A',llm=Llm())

            j_active=self.begin(val_a)
            j_done=self.begin(val_a);val_a.step({'job_id':j_done,'action':'cancel'})
            j_other_sess=self.begin(val_b)
            j_other_bot=self.begin(shi_a)

            # Legacy job file without updated_at or clarification_hops (must still load cleanly)
            legacy_id='a'*32
            (val_a.root/f'{legacy_id}.json').write_text(json.dumps({
                'owner':mod.ID,'job_id':legacy_id,'session_key':val_a.session_key(),'role':'val',
                'scope':'Legacy thesis review job','initial_plan':'Plan','confirmed':True,
                'state':'READY_EXECUTION','rounds_completed':2,'calls_attempted':8,'created_at':100.0,
            }),encoding='utf-8')

            rep=val_a.status_report({})
            active_ids=[r['job_id'] for r in rep['active_jobs']]
            comp_ids=[r['job_id'] for r in rep['completed_jobs']]
            self.assertEqual(active_ids,[j_active])
            self.assertEqual(set(comp_ids),{j_done,legacy_id})
            self.assertNotIn(j_other_sess,active_ids+comp_ids)
            self.assertNotIn(j_other_bot,active_ids+comp_ids)
            self.assertFalse(rep['retention_policy']['auto_prune_enabled'])
            self.assertEqual(rep['retention_policy']['terminal_job_max_age_days'],14)

            # Opt-in retention: dry_run leaves files intact; apply removes ONLY old unlocked terminal jobs beyond keep_recent
            preview=val_a.prune_terminal_jobs(max_age_days=14,keep_recent=1,dry_run=True)
            self.assertEqual(preview['eligible_job_ids'],[legacy_id])
            self.assertEqual(preview['pruned_count'],0)
            self.assertTrue((val_a.root/f'{legacy_id}.json').is_file())

            applied=val_a.prune_terminal_jobs(max_age_days=14,keep_recent=1,dry_run=False)
            self.assertEqual(applied['pruned_count'],1)
            self.assertFalse((val_a.root/f'{legacy_id}.json').is_file())
            self.assertTrue((val_a.root/f'{j_active}.json').is_file())
            self.assertTrue((val_a.root/f'{j_done}.json').is_file())
            self.assertTrue((shi_a.root/f'{j_other_bot}.json').is_file())

    def test_compact_council_dossier_preserves_citations_code_and_shrinks_round_two(self):
        with TemporaryDirectory() as tmp:
            filler='\n'.join(f'Background explanation paragraph line {i} repeating general framing context.' for i in range(45))
            code_block='```python\ndef chronological_holdout(series):\n    return series[:-12], series[-12:]\n```'
            cite_url='https://doi.org/10.1234/msshi-eval'
            cite_doc='doc#p12:par3'
            verbose_plan=f'Build forecast pipeline.\nCitation: {cite_url} and {cite_doc}.\n{filler}\n{code_block}'
            ev_r1=[{'source':cite_url,'summary':f'Primary baseline paper ({cite_doc}).\n{filler}'}]
            ev_r2=[{'source':'https://example.org/new-r2-check','summary':'Fresh round-2 verification result with p<0.01.'}]

            class VerboseLlm(Llm):
                def complete(self,**kwargs):
                    self.calls.append(kwargs)
                    if kwargs['task'].endswith('aggregator'):
                        bp=f'Blueprint citing {cite_url} and {cite_doc}.\n{filler}\n{code_block}'
                        return SimpleNamespace(text=json.dumps({
                            'blueprint':bp,
                            'source_requests':[{'query':'Check holdout leak','reason':'Verify split'}],
                            'limitations':['Dataset spans 24 months only'],
                        }))
                    return SimpleNamespace(text=f'Ref review noting {cite_doc} and holdout risks.')

            llm=VerboseLlm();c=self.controller(tmp,role='val',llm=llm)
            job=c.begin({'scope':'Forecast sales with chronological holdout','initial_plan':verbose_plan,'confirmed':True,'evidence':ev_r1})['job_id']
            r1=c.step({'job_id':job,'action':'council_round'})
            self.assertIn('input_telemetry',r1)
            c.step({'job_id':job,'action':'audit','message':f'Keep {cite_url} and holdout split strictly intact; verify new evidence.','evidence':ev_r2})
            r2=c.step({'job_id':job,'action':'council_round'})

            # Round 2 input must be demonstrably smaller than naive verbose re-send
            telem=r2['input_telemetry']
            self.assertLess(telem['compact_chars'],telem['naive_chars'],f'Expected Round 2 compaction: {telem}')
            self.assertGreater(telem['chars_saved'],0)

            # Inspect exact Round 2 payload sent to Reference Agent 1 (index 4 in llm.calls)
            r2_user_msg=llm.calls[4]['messages'][1]['content']
            r2_payload=json.loads(r2_user_msg)
            for key in ('goal','constraints','evidence_refs','delta_since_round_1','open_risks'):
                self.assertIn(key,r2_payload)
            # Citations, code block, new evidence, and approval boundary preserved verbatim!
            self.assertIn(cite_url,r2_user_msg)
            self.assertIn(cite_doc,r2_user_msg)
            self.assertIn('def chronological_holdout(series):',r2_user_msg)
            self.assertIn('https://example.org/new-r2-check',r2_user_msg)
            self.assertIn('Main approval is not user spending',r2_user_msg)
            self.assertEqual(len(llm.calls),8)

class ProvisionTests(unittest.TestCase):
    def setup_home(self,tmp):
        home=Path(tmp)
        for name in mod.ROLES:
            path=home/'profiles'/name;path.mkdir(parents=True)
            (path/'config.yaml').write_text('model:\n  provider: chosen-provider\n  default: chosen-main\nplugins:\n  enabled: []\n',encoding='utf-8')
        return home
    def test_install_then_idempotent_preserves_model_bytes(self):
        with TemporaryDirectory() as tmp:
            home=self.setup_home(tmp)
            before={n:(home/'profiles'/n/'config.yaml').read_bytes().split(b'plugins:')[0] for n in mod.ROLES}
            preview=provision.install(home);self.assertFalse(preview['applied'])
            actual=provision.install(home,apply=True);self.assertTrue(actual['applied'])
            for n in mod.ROLES:self.assertEqual((home/'profiles'/n/'config.yaml').read_bytes().split(b'plugins:')[0],before[n])
            self.assertEqual(provision.install(home)['files_planned'],0)
    def test_explicit_disable_and_custom_plugin_not_overwritten(self):
        with TemporaryDirectory() as tmp:
            home=self.setup_home(tmp)
            p=home/'profiles/val/config.yaml';p.write_text(p.read_text().replace('enabled: []','enabled: []\n  disabled: [msshi-interaction]'))
            folder=home/'profiles/shikaku/plugins/msshi-interaction';folder.mkdir(parents=True)
            (folder/'__init__.py').write_text('# custom user plugin')
            result=provision.install(home,apply=True)
            statuses={r['profile']:r['status'] for r in result['profiles']}
            self.assertEqual(statuses['val'],'PRESERVED_EXPLICIT_DISABLE')
            self.assertEqual(statuses['shikaku'],'PRESERVED_CUSTOM_PLUGIN_CONFLICT')
            self.assertEqual((folder/'__init__.py').read_text(),'# custom user plugin')
    def test_solo_home_does_not_create_a_team(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp);(home/'config.yaml').write_text('model:\n  provider: own\n  default: own-choice\n')
            result=provision.install_existing(home,apply=True)
            self.assertEqual(result['status'],'DEFERRED_UNTIL_FIVE_NATIVE_PROFILES')
            self.assertFalse((home/'profiles').exists());self.assertFalse((home/'plugins').exists())
    def test_fresh_academic_native_installer_provisions_all_five_roles(self):
        import contextlib,io,os
        import install_msshi
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/'HermesData';home.mkdir()
            original=b'model:\n  provider: chosen-provider\n  default: chosen-main\n'
            (home/'config.yaml').write_bytes(original)
            with patch.dict(os.environ,{'HERMES_HOME':str(home),'MSSHI_IGNORE_REGISTRY_HERMES_HOME':'1','MSSHI_NO_PDF':'1'}),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(install_msshi.main(['--platform','hermes','--mode','academic-mahasiswa','--target-dir',str(home/'profiles'),'--apply']),0)
            self.assertTrue((home/'plugins/msshi-interaction/plugin.yaml').is_file())
            for name in ('shizuka','val','kiki-chii','shikaku'):
                self.assertTrue((home/'profiles'/name/'plugins/msshi-interaction/plugin.yaml').is_file())
            self.assertEqual(provision._helpers(ROOT).load_yaml_mapping((home/'config.yaml').read_bytes())['model'],
                             provision._helpers(ROOT).load_yaml_mapping(original)['model'])
    def test_cli_family_passes_protocol_without_using_installed_old_release(self):
        import contextlib,io,os
        import msshi_cli
        with TemporaryDirectory() as tmp:
            with patch.dict(os.environ,{'MSSHI_HOME':tmp}),patch.object(msshi_cli,'active_script',return_value=None),\
                 patch.object(msshi_cli.subprocess,'call',return_value=0) as call,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(msshi_cli.main(['interaction','--protocol']),0)
            self.assertTrue(any(str(v).endswith('msshi_interaction.py') for v in call.call_args.args[0]))

if __name__=='__main__':unittest.main()
