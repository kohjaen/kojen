/**
 * @file
 * @ingroup GROUP_EXAMPLE
 * @brief   An example demonstrating code-generation abilities.
 *          CDPlayer State Machine Test Suite. Run this in the console to manually test your state machine.
 *
 *          This code is Autogenerated from 'Transition Table' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  yourname@yourdomain.com
 */

#define VERBOSE_1

using System;
using CDPlayerSM;
// {{{USER_USING_DECLARATIONS}}}
using System.Threading;
using System.Diagnostics;
// {{{USER_USING_DECLARATIONS}}}
using Xunit;

namespace CDPlayerSMTest
{
    internal class TestCDPlayerController : ICDPlayerContext
    {
        /// <summary>
        /// Test context constructor.
        /// </summary>
        internal TestCDPlayerController()
        {
            // {{{USER_CONSTRUCTOR}}}
            // {{{USER_CONSTRUCTOR}}}
        }
        /// <summary>
        /// Overridden guards.
        /// </summary>
        public virtual bool GuardCDInside()
        {
            // {{{USER_GuardCDInside}}}
            // {{{USER_GuardCDInside}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> GuardCDInside is " + ((guardCDInside) ? ("True") : ("False")));
#endif
            //return base.GuardCDInside();
            return guardCDInside;
        }
        protected bool guardCDInside = false;
        public virtual bool GuardCDHasMoreTracks()
        {
            // {{{USER_GuardCDHasMoreTracks}}}
            SetGuardHasMoreTracks();
            // {{{USER_GuardCDHasMoreTracks}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> GuardCDHasMoreTracks is " + ((guardCDHasMoreTracks) ? ("True") : ("False")));
#endif
            //return base.GuardCDHasMoreTracks();
            return guardCDHasMoreTracks;
        }
        protected bool guardCDHasMoreTracks = false;
        public virtual bool GuardCDHasNoMoreTracks()
        {
            // {{{USER_GuardCDHasNoMoreTracks}}}
            SetGuardHasMoreTracks();
            // {{{USER_GuardCDHasNoMoreTracks}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> GuardCDHasNoMoreTracks is " + ((guardCDHasNoMoreTracks) ? ("True") : ("False")));
#endif
            //return base.GuardCDHasNoMoreTracks();
            return guardCDHasNoMoreTracks;
        }
        protected bool guardCDHasNoMoreTracks = false;
        public virtual bool GuardCDHasPreviousTrack()
        {
            // {{{USER_GuardCDHasPreviousTrack}}}
            guardCDHasPreviousTrack = guardCDInside && trackCount > 0 && currentTrack > 0;
            // {{{USER_GuardCDHasPreviousTrack}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> GuardCDHasPreviousTrack is " + ((guardCDHasPreviousTrack) ? ("True") : ("False")));
#endif
            //return base.GuardCDHasPreviousTrack();
            return guardCDHasPreviousTrack;
        }
        protected bool guardCDHasPreviousTrack = false;
        /// <summary>
        /// Overridden actions.
        /// </summary>
        public virtual void OnOpenDrive(EventOpen data)
        {
            // {{{USER_OnOpenDrive_EventOpen}}}
            // {{{USER_OnOpenDrive_EventOpen}}}
            //handleOnOpenDriveOnEventOpenEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnOpenDrive on event EventOpen...");
#endif
        }
        public virtual void OnPlayTrack(EventPlay data)
        {
            // {{{USER_OnPlayTrack_EventPlay}}}
            Assert.Equal(m_expected_track_number, data.trackNo);
            // {{{USER_OnPlayTrack_EventPlay}}}
            //handleOnPlayTrackOnEventPlayEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnPlayTrack on event EventPlay...");
#endif
        }
        public virtual void OnCloseDrive(EventOpen data)
        {
            // {{{USER_OnCloseDrive_EventOpen}}}
            // {{{USER_OnCloseDrive_EventOpen}}}
            //handleOnCloseDriveOnEventOpenEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnCloseDrive on event EventOpen...");
#endif
        }
        public virtual void OnPause(EventPlay data)
        {
            // {{{USER_OnPause_EventPlay}}}
            // {{{USER_OnPause_EventPlay}}}
            //handleOnPauseOnEventPlayEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnPause on event EventPlay...");
#endif
        }
        public virtual void OnPlayNextTrack(EventEndOfTrack data)
        {
            // {{{USER_OnPlayNextTrack_EventEndOfTrack}}}
            PlayNextTrack();
            // {{{USER_OnPlayNextTrack_EventEndOfTrack}}}
            //handleOnPlayNextTrackOnEventEndOfTrackEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnPlayNextTrack on event EventEndOfTrack...");
#endif
        }
        public virtual void OnStop(EventEndOfTrack data)
        {
            // {{{USER_OnStop_EventEndOfTrack}}}
            currentTrack = 0;
            // {{{USER_OnStop_EventEndOfTrack}}}
            //handleOnStopOnEventEndOfTrackEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnStop on event EventEndOfTrack...");
#endif
        }
        public virtual void OnPlayNextTrack(EventSkipNextTrack data)
        {
            // {{{USER_OnPlayNextTrack_EventSkipNextTrack}}}
            PlayNextTrack();
            // {{{USER_OnPlayNextTrack_EventSkipNextTrack}}}
            //handleOnPlayNextTrackOnEventSkipNextTrackEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnPlayNextTrack on event EventSkipNextTrack...");
#endif
        }
        public virtual void OnPlayPreviousTrack(EventSkipPreviousTrack data)
        {
            // {{{USER_OnPlayPreviousTrack_EventSkipPreviousTrack}}}
            currentTrack = (currentTrack > 0) ? (ushort)(currentTrack - 1) : currentTrack;
            // {{{USER_OnPlayPreviousTrack_EventSkipPreviousTrack}}}
            //handleOnPlayPreviousTrackOnEventSkipPreviousTrackEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnPlayPreviousTrack on event EventSkipPreviousTrack...");
#endif
        }
        public virtual void OnStop(EventStop data)
        {
            // {{{USER_OnStop_EventStop}}}
            currentTrack = 0;
            // {{{USER_OnStop_EventStop}}}
            //handleOnStopOnEventStopEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnStop on event EventStop...");
#endif
        }
        public virtual void OnStop(EventAfter10Minutes data)
        {
            // {{{USER_OnStop_EventAfter10Minutes}}}
            currentTrack = 0;
            // {{{USER_OnStop_EventAfter10Minutes}}}
            //handleOnStopOnEventAfter10MinutesEntry.Set();
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> OnStop on event EventAfter10Minutes...");
#endif
        }
        /// <summary>
        /// Overridden on state entry/exit.
        /// </summary>
        public virtual void OnStateStopEntry()
        {
            // {{{USER_OnStateStopEntry}}}
            // {{{USER_OnStateStopEntry}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStateStopEntry...");
#endif
        }
        public virtual void OnStateStopExit()
        {
            // {{{USER_OnStateStopExit}}}
            // {{{USER_OnStateStopExit}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStateStopExit...");
#endif
        }
        public virtual void OnStateOpenEntry()
        {
            // {{{USER_OnStateOpenEntry}}}
            // {{{USER_OnStateOpenEntry}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStateOpenEntry...");
#endif
        }
        public virtual void OnStateOpenExit()
        {
            // {{{USER_OnStateOpenExit}}}
            // {{{USER_OnStateOpenExit}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStateOpenExit...");
#endif
        }
        public virtual void OnStatePlayEntry()
        {
            // {{{USER_OnStatePlayEntry}}}
            // {{{USER_OnStatePlayEntry}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStatePlayEntry...");
#endif
        }
        public virtual void OnStatePlayExit()
        {
            // {{{USER_OnStatePlayExit}}}
            // {{{USER_OnStatePlayExit}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStatePlayExit...");
#endif
        }
        public virtual void OnStatePauseEntry()
        {
            // {{{USER_OnStatePauseEntry}}}
            // {{{USER_OnStatePauseEntry}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStatePauseEntry...");
#endif
        }
        public virtual void OnStatePauseExit()
        {
            // {{{USER_OnStatePauseExit}}}
            // {{{USER_OnStatePauseExit}}}
#if VERBOSE_1
            Console.WriteLine("CDPlayer >> onStatePauseExit...");
#endif
        }
        /// <summary>
        ///
        /// </summary>
        //OsWrappers::Event handleOnOpenDriveOnEventOpenEntry;
        //OsWrappers::Event handleOnPlayTrackOnEventPlayEntry;
        //OsWrappers::Event handleOnCloseDriveOnEventOpenEntry;
        //OsWrappers::Event handleOnPauseOnEventPlayEntry;
        //OsWrappers::Event handleOnPlayNextTrackOnEventEndOfTrackEntry;
        //OsWrappers::Event handleOnStopOnEventEndOfTrackEntry;
        //OsWrappers::Event handleOnPlayNextTrackOnEventSkipNextTrackEntry;
        //OsWrappers::Event handleOnPlayPreviousTrackOnEventSkipPreviousTrackEntry;
        //OsWrappers::Event handleOnStopOnEventStopEntry;
        //OsWrappers::Event handleOnStopOnEventAfter10MinutesEntry;

        /// <summary>
        ///
        /// </summary>
        public void CheckOnOpenDriveOnEventOpenEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnOpenDriveOnEventOpenEntry.TimedWait(cEventTimeoutMs));
            //handleOnOpenDriveOnEventOpenEntry.Reset();
        }
        public void CheckOnPlayTrackOnEventPlayEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnPlayTrackOnEventPlayEntry.TimedWait(cEventTimeoutMs));
            //handleOnPlayTrackOnEventPlayEntry.Reset();
        }
        public void CheckOnCloseDriveOnEventOpenEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnCloseDriveOnEventOpenEntry.TimedWait(cEventTimeoutMs));
            //handleOnCloseDriveOnEventOpenEntry.Reset();
        }
        public void CheckOnPauseOnEventPlayEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnPauseOnEventPlayEntry.TimedWait(cEventTimeoutMs));
            //handleOnPauseOnEventPlayEntry.Reset();
        }
        public void CheckOnPlayNextTrackOnEventEndOfTrackEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnPlayNextTrackOnEventEndOfTrackEntry.TimedWait(cEventTimeoutMs));
            //handleOnPlayNextTrackOnEventEndOfTrackEntry.Reset();
        }
        public void CheckOnStopOnEventEndOfTrackEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnStopOnEventEndOfTrackEntry.TimedWait(cEventTimeoutMs));
            //handleOnStopOnEventEndOfTrackEntry.Reset();
        }
        public void CheckOnPlayNextTrackOnEventSkipNextTrackEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnPlayNextTrackOnEventSkipNextTrackEntry.TimedWait(cEventTimeoutMs));
            //handleOnPlayNextTrackOnEventSkipNextTrackEntry.Reset();
        }
        public void CheckOnPlayPreviousTrackOnEventSkipPreviousTrackEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnPlayPreviousTrackOnEventSkipPreviousTrackEntry.TimedWait(cEventTimeoutMs));
            //handleOnPlayPreviousTrackOnEventSkipPreviousTrackEntry.Reset();
        }
        public void CheckOnStopOnEventStopEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnStopOnEventStopEntry.TimedWait(cEventTimeoutMs));
            //handleOnStopOnEventStopEntry.Reset();
        }
        public void CheckOnStopOnEventAfter10MinutesEntry()
        {
            //CHECK_TRUE(cSuccess == handleOnStopOnEventAfter10MinutesEntry.TimedWait(cEventTimeoutMs));
            //handleOnStopOnEventAfter10MinutesEntry.Reset();
        }
        // {{{USER_MEMBERS}}}
        // Testing
        internal ushort m_expected_track_number = 0;
        // This could be in a base class (seems stupid to duplicate functionality here as well as in an actual controller.
        internal ushort currentTrack = 0;
        internal ushort trackCount = 0;
        internal bool isDriveOpen = false;
        internal void SetHasCD(bool has_cd)
        {
            guardCDInside = has_cd;
            Console.WriteLine("CDPlayer >> guardCDInside {0:D} ... ", has_cd);
        }
        internal void SetTrackCount(ushort trackcnt)
        {
            trackCount = trackcnt;
        }
        internal void SetIsDriveOpen(bool open)
        {
            isDriveOpen = open;
        }
        internal ushort GetTrackCount()
        {
            return trackCount;
        }
        internal ushort GetCurrentTrack()
        {
            return currentTrack;
        }
        internal void PlayNextTrack()
        {
            currentTrack = (currentTrack < trackCount) ? (ushort)(currentTrack + 1) : currentTrack;
            Console.WriteLine("CDPlayer >> PlayNextTrack {0:D} ...", currentTrack);
        }
        internal void SetGuardHasMoreTracks()
        {
            guardCDHasMoreTracks = guardCDInside && (trackCount > 0) && (currentTrack < (trackCount - 1));
            guardCDHasNoMoreTracks = !guardCDHasMoreTracks;
        }
        // {{{USER_MEMBERS}}}
    };

    /// <summary>
    /// Test Suite
    /// </summary>
    public class Suite
    {
        internal void TestCDPlayerStates()
        {
            TestCDPlayerController context = new ();
            CDPlayerStateMachine sm = new (context);
            // {{{USER_UNIT_TEST_STATES}}}
            const ushort NO_TRACKS = 10;
            Assert.True(sm.IsStateStop());
            Assert.True(!context.GuardCDInside());
            // Open the CD player
            sm.TriggerEventOpen();
            Thread.Sleep(50);
            Assert.True(sm.IsStateOpen());
            // Insert a CD and close the CD player
            sm.TriggerEventOpen();
            Thread.Sleep(50);
            // CD player motor closes the drive...an interrupt triggers that is close
            context.SetHasCD(true);
            // Read the CD info...
            context.SetTrackCount(NO_TRACKS);
            Assert.True(sm.IsStateStop());
            Assert.Equal(NO_TRACKS, context.GetTrackCount());
            Assert.Equal(0, context.GetCurrentTrack());
            Assert.True(context.GuardCDInside());
            Assert.True(context.GuardCDHasMoreTracks());
            Assert.True(!context.GuardCDHasPreviousTrack());
            ///
            /// Test : Skipping forward and backward, pause and resume, then stopping somewhere in the middle.
            /// 
            // Play the first track...
            context.m_expected_track_number = 1;
            sm.TriggerEventPlay(1);
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(0, context.GetCurrentTrack());
            // end of track.
            sm.TriggerEventEndOfTrack();
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(1, context.GetCurrentTrack());
            // end of track.
            sm.TriggerEventEndOfTrack();
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(2, context.GetCurrentTrack());
            // skip next track
            sm.TriggerEventSkipNextTrack();
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(3, context.GetCurrentTrack());
            // skip previous track
            sm.TriggerEventSkipPreviousTrack();
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(2, context.GetCurrentTrack());
            // Pause. Shouldn't matter what track is passed...
            sm.TriggerEventPlay(99);
            Thread.Sleep(50);
            Assert.True(sm.IsStatePause());
            // Resume
            context.m_expected_track_number = 5;
            sm.TriggerEventPlay(5);
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(2, context.GetCurrentTrack());
            // Stop
            sm.TriggerEventStop();
            Thread.Sleep(50);
            Assert.True(sm.IsStateStop());
            // When stopping we cleared the current track...
            Assert.Equal(0, context.GetCurrentTrack());
            ///
            /// Test : pause and automatic stop after 10 minutes.
            /// 
            context.m_expected_track_number = 25;
            sm.TriggerEventPlay(25);
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(0, context.GetCurrentTrack());
            // next track.
            sm.TriggerEventEndOfTrack();
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            Assert.Equal(1, context.GetCurrentTrack());
            // pause. Shouldn't matter what track is played
            sm.TriggerEventPlay(99);
            Thread.Sleep(50);
            Assert.True(sm.IsStatePause());
            // 10 minutes go by, and a timer interrupt signals this...
            sm.TriggerEventAfter10Minutes();
            Thread.Sleep(50);
            Assert.True(sm.IsStateStop());
            // When stopping we cleared the current track...
            Assert.Equal(0, context.GetCurrentTrack());
            ///
            /// Test : playing a whole CD goes to 'stop'.
            /// 
            context.m_expected_track_number = 15;
            sm.TriggerEventPlay(15);
            Thread.Sleep(50);
            Assert.True(sm.IsStatePlay());
            for (ushort i = 0; i <= NO_TRACKS; i++)
            {
                if (i < NO_TRACKS)
                    Assert.Equal(i, context.GetCurrentTrack());
                else
                    Assert.Equal(0, context.GetCurrentTrack());
                // end of track.
                sm.TriggerEventEndOfTrack();
                Thread.Sleep(50);
            }
            Assert.True(sm.IsStateStop());
            // When stopping we cleared the current track...
            Assert.Equal(0, context.GetCurrentTrack());
            // {{{USER_UNIT_TEST_STATES}}}
        }
        // {{{USER_TESTS}}}
        // {{{USER_TESTS}}}
        [Fact]
        public void Run() 
        {
            TestCDPlayerStates();
            // Don't forget to run your tests here.
            // {{{USER_TEST_SUITE_TESTS}}}
            // {{{USER_TEST_SUITE_TESTS}}}
        }
    };
}